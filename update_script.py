#!/usr/bin/env python
# -*- coding: utf-8 -*-

import httplib2
import json
import os


class market_lists_updater():
    def __init__(self):
        self.path_root = "cryptos/"
        self.directories_list = os.listdir('cryptos')
        self.url = {'poloniex': 'https://poloniex.com/public?command=returnTicker',
                    'bittrex': 'https://api.bittrex.com/api/v1.1/public/getmarkets'}

    def req_marketplace(self, marketplace):
        """Make request to the selected marketplace.
        marketplace : string, marketplace in url dict.
        return : json object.
        """
        if marketplace not in self.url:
            raise MarketplaceSelectionError("The marketplace you ask don't exist in self.url.")
        h = httplib2.Http('.cache')
        header, content = h.request(self.url[marketplace])
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
            print('File list for ' + marketplace + 'has been created.')
            return
        old_pairs = self.read_file(file_path)
        if pairs != old_pairs:
            print('Pairs for this marketplace are not the same as you have in your old list.')
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


    def poloniex(self):
        """Construct an ordered list of pairs for poloniex marketplace
           then compare it.
        """
        marketplace = 'poloniex'
        eth_pairs = []
        btc_pairs = []
        usdc_pairs = []
        usdt_pairs = []
        xmr_pairs = []
        all_pairs = []
        markets_dict = self.req_marketplace(marketplace)
        for pair in markets_dict:
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
        eth_pairs.sort()
        btc_pairs.sort()
        usdc_pairs.sort()
        usdt_pairs.sort()
        xmr_pairs.sort()
        all_pairs = btc_pairs + usdt_pairs + eth_pairs + usdc_pairs + xmr_pairs
        self.compare_pairs_list(marketplace, all_pairs)

    def bittrex(self):
        """Construct an ordered list of pairs for bittrex marketplace
           then compare it.
        """
        marketplace = 'bittrex'
        eth_pairs = []
        btc_pairs = []
        usd_pairs = []
        usdt_pairs = []
        all_pairs = []
        markets_resp = self.req_marketplace(marketplace)
        markets_dict = markets_resp['result']
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
            
        eth_pairs.sort()
        btc_pairs.sort()
        usd_pairs.sort()
        usdt_pairs.sort()
        all_pairs = btc_pairs + usdt_pairs + eth_pairs + usd_pairs
        self.compare_pairs_list(marketplace, all_pairs)


    def main(self):
        """Call every marketplace functions.
        """
        print("Lazy market list updater!")
        #self.poloniex()
        self.bittrex()
        print("Job done.")

updater = market_lists_updater()

if __name__ == "__main__":
    updater.main()