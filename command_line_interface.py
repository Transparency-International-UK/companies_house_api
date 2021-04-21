import argparse

parser = argparse.ArgumentParser(prog='app_scripts.py')

parser.add_argument('file', help='path to csv file with the url ids to be '
                                 'queried.')
parser.add_argument('--psc',  help='add --psc flag to get psc',
                    action="store_true")
parser.add_argument('--ol',  help='add --ol flag to get officerlist',
                    action="store_true")
parser.add_argument('--cp', help='add --cp flag to get companyprofile',
                    action="store_true")
parser.add_argument('--al', help='add --al flag to get appointmentslist',
                    action="store_true")
parser.add_argument('--ch', help='add --ch flag to get chargelist',
                    action="store_true")
parser.add_argument('--fh', help='add --fh flag to get filinghistorylist',
                    action="store_true")
