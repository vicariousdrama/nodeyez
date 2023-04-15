# import packages
import json
import logging
import requests
import optparse
import pandas as pd
from typing import Dict, Any
from LuxorLabs.resolvers import RESOLVERS

# set logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()])
    # handlers=[logging.StreamHandler(),
    #           logging.FileHandler('requests.log')]

class API:
    """
    A class used to interact with Luxor's Mining Pool GraphQL API.

    Methods
    -------
    request(query, params)
        Base function to execute operations against Luxor's GraphQL API
    
    get_subaccounts(first)
        Returns all subaccounts that belong to the Profile owner of the API Key.
        
    get_subaccount_mining_summary(subaccount, mpn, inputInterval)
        Returns an object of a subaccount mining summary.
    
    get_subaccount_hashrate_history(subaccount, mpn, inputInterval, first)
        Returns an object of a subaccount hashrate timeseries.
    
    get_worker_details_1H(subaccount, mpn, first)
        Returns object of all workers pointed to a subaccount hashrate and efficiency details in the last hour.
    
    get_worker_details_24H(subaccount, mpn, first)
        Returns object of all workers pointed to a subaccount hashrate and efficiency details in the last 24 hours.
    
    get_worker_hashrate_history(subaccount, workername, mpn, inputBucket, inputDuration, first)
        Returns an object of a miner hashrate timeseries.
    
    get_profile_active_worker_count(mpn)
        Returns an integer count of distinct Profile active workers.
    
    get_profile_inactive_worker_count(mpn)
        Returns an integer count of distinct Profile inactive workers.

    get_transaction_history(subaccount, cid, first)
        Returns on-chain transactions for a subaccount and currency combo.
    
    get_hashrate_score_history(subaccount, mpn, first)
        Returns a subaccount earnings, scoring hashrate and efficiency per day.
    
    get_revenue_ph(mpn, first)
        Returns average Hashprice per PH over the last 24H. 
    """
    def __init__(self,
                 host: str,
                 org: str,
                 key: str,
                 method: str,
                 verbose: bool = False):
        """
        Parameters
        ----------

        host : str
            Base endpoint for all API requests. Default is: https://api.cairo.luxorlabs.dev/graphql

        org : str
            Organization slug where the Profile is registered. Default is `luxor`.

        key : str
            Random generated API Key. Default is an empty string.
        
        method : str
            API request METHOD. Default is `POST`.
        
        query : str
            API request QUERY. Default is an empty string.

        params : str
            API request PARAMS. Default is an empty string.

        verbose : boolean
            Boolean flag that controls if API querys are logged.
        """

        self.host = host
        self.org = org
        self.key = key
        self.method = method
        self.verbose = verbose

    def request(self, query: str, params: Dict[str, Any] = None):
        """
        Base function to execute operations against Luxor's GraphQL API

        Parameters
        ----------
        query : str
            GraphQL compliant query string.
        params : dictionary
            dictionary containing the query parameters, values depend on query.
        """

        headers = {
            'Content-Type': 'application/json',
            'x-lux-api-key': f"{self.key}",
        }

        s = requests.Session()
        s.headers = headers
        # use tor proxy for requests
#        s.proxies = {'http': 'socks5h://127.0.0.1:9050','https': 'socks5h://127.0.0.1:9050'}
        # ssl verification because requests/ipaddress is broken?
        s.verify=False

        if self.verbose:
            logging.info(query)

        response = s.request(self.method,
                             self.host,
                             data=json.dumps({
                                 'query': query,
                                 'variables': params
                             }).encode('utf-8'))

        if response.status_code == 200:
            return response.json()
        elif response.content:
            raise Exception(
                str(response.status_code) + ": " + str(response.reason) + ": " +
                str(response.content.decode()))
        else:
            raise Exception(str(response.status_code) + ": " + str(response.reason))

    # Define API Methods
    def get_subaccounts(self, first: int) -> requests.Request:
        """
        Returns all subaccounts that belong to the Profile owner of the API Key.

        Parameters
        ----------
        first : int
            limits the number of data points returned.
        """

        query = """query getSubaccounts($first: Int) {users(first: $first) {edges {node {username}}}}"""
        params = {'first': first}

        return self.request(query, params)
    
    def get_subaccount_mining_summary(self, subaccount: str, mpn: str,
                                      inputInterval: str) -> requests.Request:
        
        """
        Returns an object of a subaccount mining summary.
        
        Parameters
        ----------
        subaccount : str
            subaccount username
        mpn : str
            mining profile name, refers to the coin ticker
        inputInterval : str
            intervals to generate the mining summary lookback, options are: `_15_MINUTE`, `_1_HOUR`, `_1_HOUR` and `_1_DAY`
        """
        
        query = """query getMiningSummary($mpn: MiningProfileName!, $userName: String!, $inputDuration: HashrateIntervals!) {
                        getMiningSummary(mpn: $mpn, userName: $userName, inputDuration: $inputDuration) {
                            hashrate
                            validShares
                            invalidShares
                            staleShares
                            badShares
                            lowDiffShares
                            revenue
                    }
                }
        """
        
        params = {
            'userName': subaccount,
            'mpn': mpn,
            'inputDuration': inputInterval
        }
        
        return self.request(query, params)

    def get_subaccount_hashrate_history(self, subaccount: str, mpn: str,
                                        inputInterval: str,
                                        first: int) -> requests.Request:
        """
        Returns an object of a subaccount hashrate timeseries.

        Parameters
        ---------
        subaccount : str
            subaccount username
        mpn : str
            mining profile name, refers to the coin ticker
        inputInterval : str
            intervals to generate the timeseries, options are: `_15_MINUTE`, `_1_HOUR`, `_6_HOUR` and `_1_DAY`
        first : int
            limits the number of data points returned
        """

        query = """query getHashrateHistory($inputUsername: String, $mpn: MiningProfileName, $inputInterval: HashrateIntervals, $first: Int) {
            getHashrateHistory(inputUsername: $inputUsername, mpn: $mpn, inputInterval: $inputInterval, first: $first) {
                edges {
                    node {
                        time
                        hashrate
                    }
                }
            }
        }"""
        params = {
            'inputUsername': subaccount,
            'mpn': mpn,
            'inputInterval': inputInterval,
            'first': first
        }

        return self.request(query, params)

    def get_worker_details_1H(self, subaccount: str, mpn: str,
                              first: int) -> requests.Request:
        """
        Returns object of all workers pointed to a subaccount hashrate and efficiency details in the last hour.
        
        Parameters
        ----------
        subaccount : str
            subaccount username
        mpn : str
            mining profile name, refers to the coin ticker
        first : int
            limits the number of data points returned
        """

        query = """query getWorkersOverview($mpn: MiningProfileName, $username: String, $first: Int) {
                    miners(filter: {
                            miningProfileName: { equalTo: $mpn }
                            user: { username: { equalTo: $username } }
                    }, first: $first) {
                        edges {
                        node {
                            workerName
                            details1H {
                                hashrate
                                status
                                efficiency
                                validShares
                                staleShares
                                badShares
                                duplicateShares
                                invalidShares
                                lowDiffShares
                            }
                        }
                    }
                }
            }"""
        params = {'username': subaccount, 'mpn': mpn, 'first': first}

        return self.request(query, params)

    def get_worker_details_24H(self, subaccount: str, mpn: str,
                               first: int) -> requests.Request:
        """
        Returns object of all workers pointed to a subaccount hashrate and efficiency details in the last 24 hours.
        
        Parameters
        ----------
        subaccount : str
            subaccount username
        mpn : str
            mining profile name, refers to the coin ticker
        first : int
            limits the number of data points returned
        """

        query = """query getWorkersOverview($mpn: MiningProfileName, $username: String, $first: Int) {
                    miners(filter: {
                            miningProfileName: { equalTo: $mpn }
                            user: { username: { equalTo: $username } }
                    }, first: $first) {
                        edges {
                        node {
                            workerName
                            details24H {
                                hashrate
                                status
                                efficiency
                                validShares
                                staleShares
                                badShares
                                duplicateShares
                                invalidShares
                                lowDiffShares
                            }
                        }
                    }
                }
            }"""
        params = {'username': subaccount, 'mpn': mpn, 'first': first}

        return self.request(query, params)

    def get_worker_hashrate_history(self, subaccount: str, workername: str, mpn: str,
                                    inputBucket: str, inputDuration: str, first: int) -> requests.Request:
        """
        Returns an object of a miner hashrate timeseries.
        
        Parameters
        ----------
        subaccount : str
            subaccount username
        workername : str
            rig identifier
        mpn : str
            mining profile name, refers to the coin ticker
        inputBucket : str
            intervals to generate the timeseries, options are: `_15_MINUTE`, `_1_HOUR`, `_6_HOUR` and `_1_DAY`
        inputDuration : str
            intervals to generate the timeseries, options are: `_15_MINUTE`, `_1_HOUR`, `_6_HOUR` and `_1_DAY`
        first : int
            limits the number of data points returned
        """

        query = """query getWorkerHashrateHistory($inputUsername: String, $workerName: String, $mpn: MiningProfileName, $inputBucket: HashrateIntervals, $inputDuration: HashrateIntervals, $first: Int) {
                    getWorkerHashrateHistory(username: $inputUsername, workerName: $workerName, mpn: $mpn, inputBucket: $inputBucket, inputDuration: $inputDuration, first: $first) {
                        edges {
                            node {
                                time
                                hashrate
                            }
                        }
                    }
                }"""

        params = {
            'inputUsername': subaccount,
            'workerName': workername,
            'mpn': mpn,
            'inputBucket': inputBucket,
            'inputDuration': inputDuration,
            'first': first
        }

        return self.request(query, params)

    def get_profile_active_worker_count(self, mpn: str) -> requests.Request:
        """
        Returns an integer count of distinct Profile active workers.
        Workers are classified as active if we recorded a share in the last 15 minutes.
        
        Parameters:
        -----------
        mpn : str
            mining profile name, refers to the coin ticker
        """

        query = """query getActiveWorkers {
                    getProfileActiveWorkers(mpn: BTC)
                }
            """
        params = {'mpn': mpn}

        return self.request(query, params)

    def get_profile_inactive_worker_count(self, mpn: str) -> requests.Request:
        """
        Returns an integer count of distinct Profile inactive workers.
        Workers are classified as inactive if we have not recorded a share in the last 15 minutes.
        
        Parameters:
        -----------
        mpn : str
            mining profile name, refers to the coin ticker
        """

        query = """query getInactiveWorkers {
                    getProfileInactiveWorkers(mpn: BTC)
                }
            """
        params = {'mpn': mpn}

        return self.request(query, params)

    def get_transaction_history(self, subaccount: str, cid: str, first: int) -> requests.Request:
        """
        Returns on-chain transactions for a subaccount and currency combo.

        Parameters
        ----------
        subaccount : str
            subaccount username
        cid : str
            currency identifier, refers to the coin ticker
        first : int
            limits the number of data points returned
        """

        query = """query getTransactionHistory($uname: String!, $cid: CurrencyProfileName!, $first: Int) {
                    getTransactionHistory(uname: $uname, cid: $cid, first: $first, orderBy: CREATED_AT_DESC) {
                        edges {
                        node {
                            createdAt
                            amount
                            status
                            transactionId
                        }
                        }
                    }
                }"""
        params = {'uname': subaccount, 'cid': cid, 'first': first}

        return self.request(query, params)

    def get_hashrate_score_history(self, subaccount: str, mpn: str, first: int) -> requests.Request:
        """
        Returns a subaccount earnings, scoring hashrate and efficiency per day.
        
        Parameters
        ----------
        subaccount : str
            subaccount username
        mpn : str
            mining profile name, refers to the coin ticker
        first : int
            limits the number of data points returned
        """

        query = """ query getHashrateScoreHistory($mpn: MiningProfileName!, $uname: String!, $first : Int) {
                    getHashrateScoreHistory(mpn: $mpn, uname: $uname, first: $first, orderBy: DATE_DESC) {
                        nodes {
                            date
                            hashrate
                            efficiency
                            revenue
                            }
                        }
                    }"""

        params = {'uname': subaccount, 'mpn': mpn, 'first': first}

        return self.request(query, params)

    def get_revenue_ph(self, mpn: str) -> requests.Request:
        """
        Returns average Hashprice per PH over the last 24H. 
        
        Parameters
        ----------
        mpn : str
            mining profile name, refers to the coin ticker
        first : int
            limits the number of data points returned
        """
        
        query = """query getRevenuePh($mpn: MiningProfileName!) {
                    getRevenuePh(mpn: $mpn)
                }
        """

        params = {'mpn': mpn}
        
        return self.request(query, params)
    
    def exec(self, method: str, params: Dict[str, Any]) -> requests.Request:
        """
        Helper function for dynamically calling functions safely.

        Parameters
        ----------
        method : str
            Class method to call
        params : dictionary
            Params to construct the method call
        """

        if hasattr(self, method) and callable(getattr(self, method)):
            func = getattr(self, method)

            args = []
            for arg in params.split(','):
                if arg.isdigit():
                    args.append(
                        int(arg)
                    )  
                    # TODO: get typed arguments. If a str param is passed with integers can be converted incorrectly as int
                else:
                    args.append(arg)

            return func(*args)

        raise Exception(f'failed to execute {method}')

if __name__ == '__main__':
    parser = optparse.OptionParser()

    parser.add_option('-e',
                      '--endpoint',
                      dest='host',
                      help='API ENDPOINT',
                      default='https://api.beta.luxor.tech/graphql')
    parser.add_option('-o',
                      '--organization',
                      dest='org',
                      help='Organization Slug',
                      default='luxor')
    parser.add_option('-k',
                      '--key',
                      dest='key',
                      help='Profile API Key',
                      default='')
    parser.add_option('-m',
                      '--method',
                      dest='method',
                      help='API Request method',
                      default='POST')
    parser.add_option('-f',
                      '--function',
                      dest='function',
                      help='API Class method',
                      default='')
    parser.add_option('-q',
                      '--query',
                      dest='query',
                      help='API Request query',
                      default='')
    parser.add_option('-p',
                      '--params',
                      dest='params',
                      help='API Request params',
                      default='')
    parser.add_option('-d',
                      '--df',
                      dest='df',
                      help='Pandas DataFrame',
                      default=False)

    options, args = parser.parse_args()

    API = API(options.host, options.org, options.key, options.method)
    RESOLVERS = RESOLVERS(options.df)

    if options.query == '':
        if options.function == '':
            raise Exception('must provide function or query')

        if not options.function in dir(API):
            raise Exception('function not found')

    params = ''
    if options.params is not None:
        params = options.params

    try:
        if options.query == '':
            resp = API.exec(options.function, options.params)
        else:
            resp = API.request(options.query, options.params)
        logging.info(resp)

    except Exception as error:
        logging.critical(error, exc_info=True)
        exit(1)

    exit(0)
