import click
from file_manager import sample_data
from suitability_score import SuitabilityScore

@click.group()
def cli():
    pass

@click.command()
@click.option("--sample-size", default=1000, prompt="Please provide the desired number of records", help="Number of drivers and streets", type=int)
def create_sample_data(sample_size):
    """This command will create sample files"""
    click.echo('Attempting to create:')
    click.echo('- drivers.txt')
    click.echo('- addresses.txt')
    sample_data(sample_size)
cli.add_command(create_sample_data, 'create-sample-data')

@click.command()
@click.option('--drivers-file', default='drivers.txt', prompt='Please input the local path to the drivers.txt file', help='The location of the custom drivers.txt file', type=click.Path(exists=True, readable=True))
@click.option('--addresses-file', default='addresses.txt', prompt='Please input the local path to the addresses.txt file', help='The location of the custom addresses.txt file', type=click.Path(exists=True, readable=True))
def calculate_suitability_score(drivers_file, addresses_file):
    """Execute the main program"""
    click.echo('Parsing files... Please wait...')
    suitability_calculator = SuitabilityScore(drivers_file, addresses_file)
    suitability_calculator.process_datasets()
    ss = suitability_calculator.get_suitability_score()
    click.echo('Total Suitability Score: ' + str(ss))
    suitability_calculator.export_csv()
cli.add_command(calculate_suitability_score, 'calculate-suitability-score')

if __name__ == '__main__':
    cli()
