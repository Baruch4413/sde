import click
from faker import Faker

def sample_data(sample_size):

    fk = Faker()

    try:
        with open(r'./addresses.txt', 'w') as fp:
            for i in range(sample_size):
                address = fk.building_number() + ' ' + fk.street_name()
                fp.write("%s\n" % address)
    except IOError:
        click.echo('Unable to create sample file: addresses.txt')


    try:
        with open(r'./drivers.txt', 'w') as fp:
            for i in range(sample_size):
                fp.write("%s\n" % fk.name())
    except IOError:
        click.echo('Unable to create sample file: drivers.txt')

