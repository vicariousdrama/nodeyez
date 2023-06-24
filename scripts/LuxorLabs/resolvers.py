# import packages
import pandas as pd
from typing import Dict, Any, Union

class RESOLVERS:
    """
    A class used to resolve (format) GraphQL API responses into a Python list 
    or Pandas DataFrame from Luxor's API.

    Methods
    -------
    resolve_get_subaccounts(json)
        Returns a formatted object of all subaccounts that belong to the Profile owner of the API Key.
    
    resolve_get_subaccount_hashrate_history(subaccount, mpn, inputInterval, first)
        Returns an object of a subaccount hashrate timeseries.
    
    resolve_get_subaccount_hashrate_history(json)
        Returns a formatted object of a subaccount hashrate timeseries. 

    resolve_get_worker_details(json)
        Returns a formatted object of all workers pointed to a subaccount hashrate and efficiency details.
        Can be used for 1H and 24H API calls.

    resolve_get_worker_hashrate_history(json)
        Returns a formatted object of a miner hashrate timeseries.

    resolve_get_profile_active_worker_count(json)
        Returns a formatted object of a Profile active workers.
        Workers are classified as active if we recorded a share in the last 15 minutes.

    resolve_get_profile_inactive_worker_count(json)
        Returns a formatted object a Profile inactive workers.
        Workers are classified as inactive if we have not recorded a share in the last 15 minutes.

    resolve_get_transaction_history(json)
        Returns a formatted object of on-chain transactions for a subaccount and currency combo.
    
    resolve_get_hashrate_score_history(json)
        Returns a formatted object of subaccount earnings, scoring hashrate and efficiency per day.
    
    resolve_get_revenue_ph(json) 
        Returns a formatted object of average Hashprice per PH over the last 24H.
    """
    def __init__(self, df: bool = False):
        """
        Parameters
        ----------
        df : boolean
            A boolean flag that determines the output of each method. Default = True.
        """

        self.df = df

    def resolve_get_subaccounts(self, json: Dict[str, Any]) -> Union[list, pd.DataFrame]:
        """
        Returns a formatted object of all subaccounts that belong to the Profile owner of the API Key.
        """

        data = [
            list(i['node'].values())[0] for i in json['data']['users']['edges']
        ]

        if self.df:
            return pd.DataFrame([data], columns=['subaccounts'])
        else:
            return data
    
    def resolve_get_subaccount_mining_summary(self, json: Dict[str, Any]) -> Union[list, pd.DataFrame]:
        """
        Returns a formatted object of a subaccount hashrate timeseries.
        """
        
        data = json['data']['getMiningSummary']
        
        if self.df:
            return pd.DataFrame(data, columns=['hashrate', 'validShares', 'invalidShares', 'staleShares', 'badShares', 'lowDiffShares', 'revenue'], index = [0])
        else:
            return data

    def resolve_get_subaccount_hashrate_history(self, json: Dict[str, Any]) -> Union[list, pd.DataFrame]:
        """
        Returns a formatted object of a subaccount hashrate timeseries. 
        """

        data = [
            list(i['node'].values())
            for i in json['data']['getHashrateHistory']['edges']
        ]

        if self.df:
            return pd.DataFrame(data, columns=['timestamp', 'hashrate'])

        return data

    def resolve_get_worker_details(self, json: Dict[str, Any]) -> Union[list, pd.DataFrame]:
        """
        Returns a formatted object of all workers pointed to a subaccount hashrate and efficiency details.
        Can be used for 1H and 24H API calls.
        """

        data = [
            list(i['node'].values()) for i in json['data']['miners']['edges']
        ]

        if self.df:
            return pd.concat([
                pd.DataFrame([i[0] for i in data], columns=['workerNames']),
                pd.DataFrame.from_dict([i[1] for i in data])
            ],
                             axis=1)
        return data

    def resolve_get_worker_hashrate_history(self, json: Dict[str, Any]) -> Union[list, pd.DataFrame]:
        """
        Returns a formatted object of a miner hashrate timeseries.
        """

        data = [
            list(i['node'].values())
            for i in json['data']['getWorkerHashrateHistory']['edges']
        ]

        if self.df:
            return pd.DataFrame(data, columns=['timestamp', 'hashrate'])
        
        return data

    def resolve_get_profile_active_worker_count(self, json: Dict[str, Any]) -> Union[list, pd.DataFrame]:
        """
        Returns a formatted object of a Profile active workers.
        Workers are classified as active if we recorded a share in the last 15 minutes.
        """

        if self.df:
            return pd.DataFrame([json['data']['getProfileActiveWorkers']],
                                columns=['activeWorkers'])
        
        return json['data']['getProfileActiveWorkers']

    def resolve_get_profile_inactive_worker_count(self, json: Dict[str, Any]) -> Union[list, pd.DataFrame]:
        """
        Returns a formatted object a Profile inactive workers.
        Workers are classified as inactive if we have not recorded a share in the last 15 minutes.
        """

        if self.df:
            return pd.DataFrame([json['data']['getProfileInactiveWorkers']],
                                columns=['inactiveWorkers'])
        
        return json['data']['getProfileInactiveWorkers']

    def resolve_get_transaction_history(self, json: Dict[str, Any]) -> Union[list, pd.DataFrame]:
        """
        Returns a formatted object of on-chain transactions for a subaccount and currency combo.
        """

        data = [
            list(i['node'].values())
            for i in json['data']['getTransactionHistory']['edges']
        ]

        if self.df:
            return pd.DataFrame(
                data,
                columns=['createdAt', 'amount', 'status', 'Transaction ID'])
        
        return data

    def resolve_get_hashrate_score_history(self, json: Dict[str, Any]) -> Union[list, pd.DataFrame]:
        """
        Returns a formatted object of subaccount earnings, scoring hashrate and efficiency per day.
        """

        data = [
            list(i.values()) for i in json['data']['getHashrateScoreHistory']['nodes']
        ]

        if self.df:
            return pd.DataFrame(
                data,
                columns = ['date', 'hashrate', 'efficiency', 'revenue']
            )
        
        return data

    def resolve_get_revenue_ph(self, json: Dict[str, Any]) -> Union[list, pd.DataFrame]:
        """
        Returns a formatted object of average Hashprice per PH over the last 24H.
        """
        
        data = json['data']        
        if self.df:
            return pd.DataFrame(data, index=[0])
        else:
            return data['getRevenuePh']