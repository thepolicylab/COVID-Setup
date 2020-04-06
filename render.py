import json
import io
import os
import tempfile
from contextlib import contextmanager
from pathlib import Path

import click
import geopandas as gpd
import jinja2
import numpy as np
import pandas as pd
import requests
import us
import yaml
from census import Census


BASE_URL_2010 = 'https://www2.census.gov/geo/tiger/TIGER2010/COUNTY/2010/tl_2010_{fips}_county10.zip'
BASE_URL_GT_2010 = 'https://www2.census.gov/geo/tiger/TIGER2011/COUNTY/tl_{year}_us_county.zip'


@contextmanager
def cache_directory(use_cache: bool):
  """
  This is a simple switch of a cache directory. If use_cache is True,
  we yield the cache directory, which is just .cache. If not, then
  we create a TemporaryDirectory and yield that.

  In each case, a Path is yielded.
  """
  CACHE_DIRECTORY = Path('.cache')
  if use_cache:
    if not CACHE_DIRECTORY.exists():
      CACHE_DIRECTORY.mkdir()
    yield CACHE_DIRECTORY
  else:
    with tempfile.TemporaryDirectory() as tmpdir:
      yield Path(tmpdir)


@click.group()
def cli():
  pass


@cli.command('report')
@click.option(
  '-c', '--config', 'config_file',
  envvar='CONFIG_PATH', type=click.Path(exists=True), required=True,
  help='configuration file for this simulation'
)
@click.option(
  '-o', '--output', 'output_file',
  type=click.File('wt'), default='-',
  help="Where the output should be stored. Default is stdout"
)
def report_command(config_file: str, output_file: io.TextIOWrapper):
  """ Create a report template """
  with open(config_file, 'rt') as infile:
    config = yaml.safe_load(infile)

  # TODO(khw): Set this up for packaging
  environment = jinja2.Environment(
    loader = jinja2.FileSystemLoader(os.path.dirname(__file__)),
    lstrip_blocks=True,
    trim_blocks=True
  )

  template = environment.get_template('base_report.Rmd.j2')
  print(template.render(single_state=config['spatial_setup']['single_state']), file=output_file)

@cli.command('mobility')
@click.option(
  '-c', '--config', 'config_file',
  envvar='CONFIG_PATH', type=click.Path(exists=True), required=True,
  help='configuration file for this simulation'
)
@click.option(
  '--use-cache/--no-use-cache', default=False,
  help='Use a local cache directory (.cache) for Census API data'
)
def import_mobility(config_file: str, use_cache: bool):
  """ Create the mobility data """
  COMMUTATE_DATA_FILE = 'commute_data.parquet'

  with open(config_file, 'rt') as infile:
    config = yaml.safe_load(infile)

  c = Census(config['importation']['census_api_key'])
  census_year = config['spatial_setup']['census_year']

  spatial_setup = config['spatial_setup']
  states = spatial_setup['modeled_states']

  output_path = Path(spatial_setup['base_path'])
  geodata_path = output_path / spatial_setup['geodata']
  mobility_path = output_path / spatial_setup['mobility']

  fips_to_state = {us.states.lookup(state).fips: state for state in states}
  state_fips = list(fips_to_state.keys())

  print('Opening commute data')
  commute_data = pd.read_parquet(COMMUTATE_DATA_FILE)
  print('Done reading data. Manipulating...')
  commute_data['OSTATEFP'] = commute_data['OFIPS'].str[:2]
  commute_data['DSTATEFP'] = commute_data['DFIPS'].str[:2]
  commute_data['OCOUNTYFP'] = commute_data['OFIPS'].str[:5]
  commute_data['DCOUNTYFP'] = commute_data['DFIPS'].str[:5]
  print('Done manipulating. Now filtering')

  # Filter commute data to relevant states
  commute_data = commute_data[
    commute_data['OSTATEFP'].isin(state_fips) &
    commute_data['DSTATEFP'].isin(state_fips)
  ]

  data = []
  for fips, state in fips_to_state.items():
    print(f'Pulling data for {state}')

    # TODO(khw): Can tighten up around use of cache directory here
    with cache_directory(use_cache) as CACHE_DIRECTORY:
      cache_file = CACHE_DIRECTORY / f'population_{state}_{census_year}.json'
      if cache_file.exists():
        with open(cache_file) as infile:
          datum = json.load(infile)
      else:
        print(f'{state} not present in cache. Pulling from Census API')
        datum = c.acs.state_county('B01003_001E', fips, '*', year=census_year)
        with open(cache_file, 'wt') as outfile:
          json.dump(datum, outfile)
    data.extend(datum)
  print('Done pulling data')

  census_df = pd.DataFrame(data)
  census_df['COUNTYFP'] = census_df['state'] + census_df['county']

  geodata = pd.DataFrame({
    'geoid': census_df['COUNTYFP'].apply(int),  # TODO(khw): This int is the source of later bugs
    'pop2010': census_df['B01003_001E'].apply(int),
    'stateUSPS': census_df['state'].map(fips_to_state)
  }).sort_values('geoid')

  print('Computing mobility')
  commute_by_county = commute_data.groupby(['OCOUNTYFP', 'DCOUNTYFP'])['FLOW'].sum().reset_index()
  mobility_df = commute_by_county.pivot_table(
    index='OCOUNTYFP', columns='DCOUNTYFP', values='FLOW', aggfunc='sum', fill_value=0.0
  )

  # Make sure that everything is consistently sorted
  mobility_df = mobility_df.sort_index().sort_index(axis=1)
  mobility = mobility_df.values
  mobility += mobility.T  # Symetric mobility doubling fluxes mobility.sum is around 5M which is a bit low
  np.fill_diagonal(mobility, 0)

  print('Saving files')
  if not output_path.exists():
    output_path.mkdir()
  geodata.to_csv(geodata_path, index=False)
  np.savetxt(str(mobility_path), mobility)
  print('Done')


@cli.command('shapefile')
@click.option(
  '-c', '--config', 'config_file',
  envvar='CONFIG_PATH', type=click.Path(exists=True), required=True,
  help='configuration file for this simulation'
)
@click.option(
  '--use-cache/--no-use-cache', default=False,
  help='Use a local cache directory (.cache) for Census API data'
)
def pull_shapefiles(config_file: str, use_cache: bool):
  """
  Create shapefiles as expected by repository
  """
  with open(config_file, 'rt') as infile:
    config = yaml.safe_load(infile)

  spatial_config = config['spatial_setup']
  spatial_base_path = Path(spatial_config['base_path'])

  modeled_states = spatial_config['modeled_states']

  census_year = int(spatial_config['census_year'])
  if census_year < 2010 or census_year > 2018:
    raise click.BadParameter("census_year must be between 2010 and 2018")

  if census_year == 2010:
    gdfs = []
    with cache_directory(use_cache) as tmpdir:
      for state_abbr in modeled_states:
        state = us.states.lookup(state_abbr)
        fips = state.fips
        fips_file = tmpdir / f'fips_{fips}.zip'
        # Check if the file is in the cache
        if not fips_file.exists():
          with open(fips_file, 'wb') as outfile:
            response = requests.get(BASE_URL_2010.format(fips=fips), stream=True)
            for block in response.iter_content(1024):
              outfile.write(block)
            
        gdf = gpd.read_file(f'zip://{fips_file.absolute()}')
        gdf['state_abbr'] = state_abbr
        gdfs.append(gdf)
    gdf = pd.concat(gdfs)

    for col in ['STATEFP', 'COUNTYFP', 'GEOID', 'NAME']:
      gdf[col] = gdf[f'{col}10']
      gdf['NAME'] = gdf['NAME10'] + " County, " + gdf.state_abbr
  
  else:
    # We're sometime after 2010 when the file format changed
    with cache_directory(use_cache) as tmpdir:
      fips_file = (Path(tmpdir) / 'all_fips.zip').absolute()
      # Check if the file is in the cache
      if not fips_file.exists():
        with open(fips_file, 'wb') as outfile:
          response = requests.get(BASE_URL_GT_2010.format(year=census_year))
          for block in response.iter_content(1024):
            outfile.write(block)
      gdf = gpd.read_file(f'zip://{fips_file}')
      gdf = pd.DataFrame({
        'state_abbr': modeled_states,
        'STATEFP': [us.states.lookup(state).fips for state in modeled_states]
      }).merge(gdf, on='STATEFP')

      gdf['NAME'] = gdf['NAME'] + " County, " + gdf['state_abbr']

  gdf['GEOID'] = gdf.GEOID.astype(int)  # This should make everything consistent
  gdf.to_file(spatial_base_path / spatial_config['shapefile'])


@cli.command('makefile')
@click.option(
  '-c', '--config', 'config_file',
  envvar='CONFIG_PATH', type=click.Path(exists=True), required=True,
  help='Configuration file for this simulation'
)
@click.option(
  '-o', '--output', 'output_file',
  type=click.File('wt'), default='-',
  help="Where the output should be stored. Default is stdout"
)
def render_makefile(config_file: str, output_file: io.TextIOWrapper):
  """ Render the makefile """
  with open(config_file) as infile:
    config = yaml.safe_load(infile)

  output_base = config['name']
  num_sims = config.get('nsimulations', 10)
  num_cores = config.get('ncores', 1)
  simulation_names = config.get('interventions', {}).get('scenarios', [])
  death_rate_names = config.get('hospitalization', {}).get('parameters', {}).get('p_death_names', [])

  # TODO(khw): Set this up for packaging
  environment = jinja2.Environment(
    loader = jinja2.FileSystemLoader(os.path.dirname(__file__)),
    lstrip_blocks=True,
    trim_blocks=True
  )

  def format_string(value, the_format="{}"):
    return the_format.format(value)

  environment.filters['format_string'] = format_string
  template = environment.get_template("Makefile.j2")
  print(template.render(
    num_sims=num_sims,
    num_cores=num_cores,
    output_base=output_base,
    simulation_names=simulation_names,
    death_rate_names=death_rate_names,
    config_path=config_file
  ), file=output_file)


if __name__ == '__main__':
  cli()