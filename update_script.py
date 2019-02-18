#!/usr/bin/env python
# -*- coding: utf-8 -*-

import httplib2
import json
import os


class market_lists_updater():
    def __init__(self):
        self.path_root = "cryptos/"
        self.directories_list = os.listdir('cryptos')
        self.new_pairs_list = [] # Ugly but working
        self.marketplace_obj = {'poloniex': 'https://poloniex.com/public?command=returnTicker',
                                'bittrex' : 'https://api.bittrex.com/api/v1.1/public/getmarkets',
                                'binance' : 'https://api.binance.com/api/v1/exchangeInfo',
                                'bitfinex': 'https://api-pub.bitfinex.com/v2/tickers?symbols=ALL'}

    def req_marketplace(self, marketplace):
        """Make request to the selected marketplace.
        marketplace : string, marketplace in marketplace_obj dict.
        return : json object.
        """
        if marketplace not in self.marketplace_obj:
            raise MarketplaceSelectionError("The marketplace you ask don't exist in self.marketplace_obj.")
        h = httplib2.Http('.cache')
        header, content = h.request(self.marketplace_obj[marketplace])
        data = self.format_response(content)
        return data


    def format_response(self, resp):
        """Read & format http request.
        resp : byte, content returned by a http GET.
        return : json object, formated data.
        """
        data = json.loads(resp.decode('utf-8'))
        if 'error' in data:
            raise ApiError(data['error'])
        return data

    def construct_file_path(self, marketplace):
        """Check if the directory exist and construct the file path.
        marketplace : string, marketplace name.
        return: string, constructed file path.
        """
        if marketplace not in self.directories_list:
            os.makedirs(self.path_root + marketplace)
            print('The directory for ' + marketplace + ' has been created.')
        file_path = self.path_root + marketplace + '/' + marketplace + \
                    '_pair_list.txt'
        return file_path

    def compare_pairs_list(self, marketplace, pairs):
        """Check if a file for the pairs list exist and update if needed.
        marketplace : string, marketplace name.
        pairs : list, all of the actual pairs of the marketplace.
        """
        file_path = self.construct_file_path(marketplace)
        if not os.path.isfile(file_path):
            self.write_file(file_path, pairs)
            print('Pairs list file for ' + marketplace + ' has been created.')
            return
        old_pairs = self.read_file(file_path)
        if pairs != old_pairs:
            print('Your local pairs list has been updated for ' + marketplace + '.')
            self.write_file(file_path, pairs)
        else:
            print('No change needed for ' + marketplace + ' list.')


    def read_file(self, file_path):
        """Read file and format data.
        file_path : string, path of the file.
        return : list, contain all pairs stored localy.
        """
        old_pairs = []
        with open(file_path, mode='r', encoding='utf-8') as pairs_file:
            for line in pairs_file:
                line = line.replace(',\n', '')
                old_pairs.append(line)
        return old_pairs

    def write_file(self, file_path, pairs):
        """Write file and format data.
        file_path : string, path of the file.
        pairs : list, contain all pairs newly updated.
        """
        with open(file_path, mode='w', encoding='utf-8') as pairs_file:
            for pair in pairs:
                pairs_file.write(pair + ',\n')


    def poloniex(self, marketplace, api_json):
        """Construct an ordered list of pairs for poloniex marketplace
           then compare it.
           api_json : json, non ordered list from marketplace.
           return : list, ordered list of pairs from marketplace api.
        """
        btc_pairs = []
        eth_pairs = []
        usdc_pairs = []
        usdt_pairs = []
        xmr_pairs = []
        all_pairs = []
        for pair in api_json:
            if pair[:3] == 'BTC':
                pair = pair.replace('BTC_', marketplace.upper() + ':')
                pair += 'BTC'
                btc_pairs.append(pair)
                continue
            if pair[:3] == 'ETH':
                pair = pair.replace('ETH_', marketplace.upper() + ':')
                pair += 'ETH'
                eth_pairs.append(pair)
                continue
            if pair[:4] == 'USDC':
                pair = pair.replace('USDC_', marketplace.upper() + ':')
                pair += 'USDC'
                usdc_pairs.append(pair)
                continue
            if pair[:4] == 'USDT':
                pair = pair.replace('USDT_', marketplace.upper() + ':')
                pair += 'USDT'
                usdt_pairs.append(pair)
                continue
            if pair[:3] == 'XMR':
                pair = pair.replace('XMR_', marketplace.upper() + ':')
                pair += 'XMR'
                xmr_pairs.append(pair)
                continue
        btc_pairs.sort()
        eth_pairs.sort()
        usdc_pairs.sort()
        usdt_pairs.sort()
        xmr_pairs.sort()
        all_pairs = btc_pairs + usdt_pairs + eth_pairs + usdc_pairs + xmr_pairs
        #return all_pairs # I wasn't able to return data from exec in main, need to be solved
        self.new_pairs_list = all_pairs

    def bittrex(self, marketplace, api_json):
        """Construct an ordered list of pairs for bittrex marketplace
           then compare it.
           api_json : json, non ordered list from marketplace.
           return : list, ordered list of pairs from marketplace api.
        """
        btc_pairs = []
        eth_pairs = []
        usd_pairs = []
        usdt_pairs = []
        all_pairs = []
        markets_dict = api_json['result']
        for obj in markets_dict:
            pair = obj['MarketName']
            if pair[:3] == 'BTC':
                pair = pair.replace('BTC-', marketplace.upper() + ':')
                pair += 'BTC'
                btc_pairs.append(pair)
                continue
            if pair[:3] == 'ETH':
                pair = pair.replace('ETH-', marketplace.upper() + ':')
                pair += 'ETH'
                eth_pairs.append(pair)
                continue
            if pair[:4] == 'USDT':
                pair = pair.replace('USDT-', marketplace.upper() + ':')
                pair += 'USDT'
                usdt_pairs.append(pair)
                continue
            if pair[:3] == 'USD':
                pair = pair.replace('USD-', marketplace.upper() + ':')
                pair += 'USD'
                usd_pairs.append(pair)
                continue
        btc_pairs.sort()
        eth_pairs.sort()
        usd_pairs.sort()
        usdt_pairs.sort()
        all_pairs = btc_pairs + usdt_pairs + eth_pairs + usd_pairs
        #return all_pairs # I wasn't able to return data from exec in main, need to be solved
        self.new_pairs_list = all_pairs

    def binance(self, marketplace, api_json):
        """Construct an ordered list of pairs for binance marketplace
           then compare it.
           api_json : json, non ordered list from marketplace.
           return : list, ordered list of pairs from marketplace api.
        """
        bnb_pairs = []
        btc_pairs = []
        eth_pairs = []
        usdt_pairs = []
        xrp_pairs = []
        all_pairs = []
        markets_dict = api_json['symbols']
        for obj in markets_dict:
            pair = obj['symbol']
            if pair[-3:] == 'BNB':
                pair = marketplace.upper() + ':' + pair
                bnb_pairs.append(pair)
                continue
            if pair[-3:] == 'BTC':
                pair = marketplace.upper() + ':' + pair
                btc_pairs.append(pair)
                continue
            if pair[-3:] == 'ETH':
                pair = marketplace.upper() + ':' + pair
                eth_pairs.append(pair)
                continue
            if pair[-4:] == 'USDT':
                pair = marketplace.upper() + ':' + pair
                usdt_pairs.append(pair)
                continue
            if pair[-3:] == 'XRP':
                pair = marketplace.upper() + ':' + pair
                xrp_pairs.append(pair)
                continue
        bnb_pairs.sort()
        btc_pairs.sort()
        eth_pairs.sort()
        usdt_pairs.sort()
        xrp_pairs.sort()
        all_pairs = btc_pairs + usdt_pairs + eth_pairs + bnb_pairs + xrp_pairs
        #return all_pairs # I wasn't able to return data from exec in main, need to be solved
        self.new_pairs_list = all_pairs

    def bitfinex(self, marketplace, api_json):
        """Construct an ordered list of pairs for bitfinex marketplace
           then compare it.
           api_json : json, non ordered list from marketplace.
           return : list, ordered list of pairs from marketplace api.
        """
        btc_pairs = []
        eth_pairs = []
        eur_pairs = []
        eos_pairs = []
        dai_pairs = []
        gbp_pairs = []
        jpy_pairs = []
        usd_pairs = []
        xlm_pairs = []
        all_pairs = []
        for pair in api_json:
            if pair[0][:1] == 't':
                if pair[0][-3:] == 'BTC':
                    pair = pair[0].replace('t', marketplace.upper() + ':')
                    btc_pairs.append(pair)
                    continue
                if pair[0][-3:] == 'ETH':
                    pair = pair[0].replace('t', marketplace.upper() + ':')
                    eth_pairs.append(pair)
                    continue
                if pair[0][-3:] == 'EUR':
                    pair = pair[0].replace('t', marketplace.upper() + ':')
                    eur_pairs.append(pair)
                    continue
                if pair[0][-3:] == 'EOS':
                    pair = pair[0].replace('t', marketplace.upper() + ':')
                    eos_pairs.append(pair)
                    continue
                if pair[0][-3:] == 'DAI':
                    pair = pair[0].replace('t', marketplace.upper() + ':')
                    dai_pairs.append(pair)
                    continue
                if pair[0][-3:] == 'GBP':
                    pair = pair[0].replace('t', marketplace.upper() + ':')
                    gbp_pairs.append(pair)
                    continue
                if pair[0][-3:] == 'jpy':
                    pair = pair[0].replace('t', marketplace.upper() + ':')
                    jpy_pairs.append(pair)
                    continue
                if pair[0][-3:] == 'USD':
                    pair = pair[0].replace('t', marketplace.upper() + ':')
                    usd_pairs.append(pair)
                    continue
                if pair[0][-3:] == 'XLM':
                    pair = pair[0].replace('t', marketplace.upper() + ':')
                    xlm_pairs.append(pair)
                    continue
        btc_pairs.sort()
        eth_pairs.sort()
        eur_pairs.sort()
        eos_pairs.sort()
        dai_pairs.sort()
        gbp_pairs.sort()
        jpy_pairs.sort()
        usd_pairs.sort()
        xlm_pairs.sort()
        all_pairs = btc_pairs + usd_pairs + eth_pairs + eur_pairs + jpy_pairs + \
                    gbp_pairs +jpy_pairs + dai_pairs + eos_pairs + xlm_pairs
        print(all_pairs)
        #return all_pairs # I wasn't able to return data from exec in main, need to be solved
        self.new_pairs_list = all_pairs


    def main(self):
        """Call every marketplace functions.
        """
        print("Lazy market list updater!")
        for marketplace in self.marketplace_obj:
            new_list = self.req_marketplace(marketplace)
            exec('self.' + marketplace + '(marketplace, new_list)')
            self.compare_pairs_list(marketplace, self.new_pairs_list)

        print("Job done.")

updater = market_lists_updater()

if __name__ == "__main__":
    updater.main()