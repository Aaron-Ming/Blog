from s2p import S2P
from configobj import ConfigObj
from os.path import join,dirname,abspath,exists
__all__ = ['MYSQL', 'PRODUCT', 'GLOBAL']

GLOBAL, PRODUCT, MYSQL = {},{},{}

ConfigFile=join(dirname(dirname(abspath(__file__))), 'config.ini')
if not exists(ConfigFile): raise OSError('No config file config.ini')

ParserConfig     = lambda section,var: ConfigObj(ConfigFile).get(section).get(var)
ParserConfigDict = lambda section,var: S2P(f=ConfigFile, section=section).ToDict(var=var)
ParserConfigList = lambda section,var: S2P(f=ConfigFile, section=section).ToDict(var=var)

GLOBAL['Environment']      = ParserConfig('global', 'Environment')
GLOBAL['Host']             = ParserConfig('global', 'Host')
GLOBAL['Port']             = ParserConfig('global', 'Port')
GLOBAL['Debug']            = ParserConfig('global', 'Debug')
GLOBAL['LogLevel']         = ParserConfig('global', 'LogLevel')
PRODUCT['ProcessName']     = ParserConfig('product', 'ProcessName')
PRODUCT['ProductType']     = ParserConfig('product', 'ProductType')
PRODUCT['ApplicationHome'] = ParserConfig('product', 'ApplicationHome')
MYSQL['MySQLConnection']   = ParserConfigDict('mysql', 'MySQLConnection')

if __name__ == "__main__":
    import json
    print json.dumps(GLOBAL)
