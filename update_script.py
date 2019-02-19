#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import os


class market_lists_updater():
    def __init__(self):
        self.path_root = "cryptos/"
        self.new_pairs_list = [] # Ugly but working
        self.marketplace_obj = {'poloniex': 'https://poloniex.com/public?command=returnTicker',
                                'bittrex' : 'https://api.bittrex.com/api/v1.1/public/getmarkets',
                                'binance' : 'https://api.binance.com/api/v1/exchangeInfo',
                                'bitfinex': 'https://api-pub.bitfinex.com/v2/tickers?symbols=ALL',
                                'kraken'  : 'https://api.kraken.com/0/public/AssetPairs',
                                'bitstamp': 'https://www.bitstamp.net/api/v2/trading-pairs-info/',
                                'okcoin'  : 'https://www.okcoin.com/api/spot/v3/instruments/',
                                'coinbase': 'https://api.pro.coinbase.com/products',
                                'bitmex'  : 'https://bitmex.com/api/v1/instrument/active'} 

    def root_repository_failsafe(self):
        path_root = self.path_root.replace('/', '')
        if 'cryptos' not in os.listdir():
            os.makedirs('cryptos')
            print('cryptos directory was missing and has been created')

    def req_marketplace(self, marketplace):
        """Make request to the selected marketplace.
        marketplace : string, marketplace in marketplace_obj dict.
        return : json object.
        """
        if marketplace not in self.marketplace_obj:
            raise MarketplaceSelectionError("The marketplace you ask don't exist in self.marketplace_obj.")
        r = requests.get(self.marketplace_obj[marketplace])
        if r.status_code not in (200, 201, 202):
            r.raise_for_status()
        r = r.json()
        return r

    def construct_file_path(self, marketplace, margin='no'):
        """Check if the directory exist and construct the file path.
        marketplace : string, marketplace name.
        return: string, constructed file path.
        """
        directories_list = os.listdir(self.path_root.replace('/', ''))
        if marketplace not in directories_list:
            os.makedirs(self.path_root + marketplace)
            print('The directory for ' + marketplace + ' has been created.')
        if margin != 'no':
            file_path = self.path_root + marketplace + '/' + marketplace + \
                    '_margin_pair_list.txt'
        else:
            file_path = self.path_root + marketplace + '/' + marketplace + \
                        '_pair_list.txt'
        return file_path

    def compare_pairs_list(self, marketplace, file_path, pairs):
        """Check if a file for the pairs list exist and update if needed.
        marketplace : string, marketplace name.
        pairs : list, all of the actual pairs of the marketplace.
        """
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
                pair = pair.replace('BTC_', marketplace.upper() + ':') + 'BTC'
                btc_pairs.append(pair)
                continue
            if pair[:3] == 'ETH':
                pair = pair.replace('ETH_', marketplace.upper() + ':') + 'ETH'
                eth_pairs.append(pair)
                continue
            if pair[:4] == 'USDC':
                pair = pair.replace('USDC_', marketplace.upper() + ':') + 'USDC'
                usdc_pairs.append(pair)
                continue
            if pair[:4] == 'USDT':
                pair = pair.replace('USDT_', marketplace.upper() + ':') + 'USDT'
                usdt_pairs.append(pair)
                continue
            if pair[:3] == 'XMR':
                pair = pair.replace('XMR_', marketplace.upper() + ':') + 'XMR'
                xmr_pairs.append(pair)
                continue
        btc_pairs.sort()
        eth_pairs.sort()
        usdc_pairs.sort()
        usdt_pairs.sort()
        xmr_pairs.sort()
        all_pairs = usdt_pairs + btc_pairs + eth_pairs + usdc_pairs + xmr_pairs
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
                pair = pair.replace('BTC-', marketplace.upper() + ':') + 'BTC'
                btc_pairs.append(pair)
                continue
            if pair[:3] == 'ETH':
                pair = pair.replace('ETH-', marketplace.upper() + ':') + 'ETH'
                eth_pairs.append(pair)
                continue
            if pair[:4] == 'USDT':
                pair = pair.replace('USDT-', marketplace.upper() + ':') + 'USDT'
                usdt_pairs.append(pair)
                continue
            if pair[:3] == 'USD':
                pair = pair.replace('USD-', marketplace.upper() + ':') + 'USD'
                usd_pairs.append(pair)
                continue
        btc_pairs.sort()
        eth_pairs.sort()
        usd_pairs.sort()
        usdt_pairs.sort()
        all_pairs = usdt_pairs + btc_pairs + eth_pairs + usd_pairs
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
        all_pairs = usdt_pairs + btc_pairs + eth_pairs + bnb_pairs + xrp_pairs
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
        all_pairs = usd_pairs + btc_pairs + eth_pairs + eur_pairs + jpy_pairs + \
                    gbp_pairs +jpy_pairs + dai_pairs + eos_pairs + xlm_pairs
        #return all_pairs # I wasn't able to return data from exec in main, need to be solved
        self.new_pairs_list = all_pairs

    def kraken(self, marketplace, api_json):
        """Construct an ordered list of pairs for kraken marketplace
           then compare it.
           api_json : json, non ordered list from marketplace.
           return : list, ordered list of pairs from marketplace api.
        """
        btc_pairs = []
        btc_margin_pairs = []
        cad_pairs = []
        eth_pairs = []
        eth_margin_pairs = []
        eur_pairs = []
        eur_margin_pairs = []
        jpy_pairs = []
        usd_pairs = []
        usd_margin_pairs = []
        all_pairs = []
        all_margin_pairs = []
        markets_dict = api_json['result']
        for pair in markets_dict:
            market_pair = pair
            if pair[-3:] == 'XBT':
                pair = marketplace.upper() + ':' + pair
                btc_pairs.append(pair)
                if markets_dict[market_pair]['leverage_buy'] != []:
                    btc_margin_pairs.append(pair)
                continue
            if pair[-3:] == 'CAD':
                pair = marketplace.upper() + ':' + pair
                cad_pairs.append(pair)
                continue
            if pair[-3:] == 'ETH':
                pair = marketplace.upper() + ':' + pair
                eth_pairs.append(pair)
                if markets_dict[market_pair]['leverage_buy'] != []:
                    eth_margin_pairs.append(pair)
                continue
            if pair[-3:] == 'EUR':
                pair = marketplace.upper() + ':' + pair
                eur_pairs.append(pair)
                if markets_dict[market_pair]['leverage_buy'] != []:
                    eur_margin_pairs.append(pair)
                continue
            if pair[-3:] == 'JPY':
                pair = marketplace.upper() + ':' + pair
                jpy_pairs.append(pair)
                continue
            if pair[-3:] == 'USD':
                pair = marketplace.upper() + ':' + pair
                usd_pairs.append(pair)
                if markets_dict[market_pair]['leverage_buy'] != []:
                    eur_margin_pairs.append(pair)
                continue
        btc_pairs.sort()
        btc_margin_pairs.sort()
        cad_pairs.sort()
        eth_pairs.sort()
        eth_margin_pairs.sort()
        eur_pairs.sort()
        eur_margin_pairs.sort()
        jpy_pairs.sort()
        usd_pairs.sort()
        usd_margin_pairs.sort()
        all_pairs = btc_pairs + eur_pairs + usd_pairs + eth_pairs + cad_pairs + jpy_pairs
        all_margin_pairs = eur_margin_pairs + usd_margin_pairs + btc_margin_pairs \
                           + eth_margin_pairs
        #return all_pairs # I wasn't able to return data from exec in main, need to be solved
        self.new_pairs_list = all_pairs
        file_path = self.construct_file_path(marketplace, 'yes')
        self.compare_pairs_list(marketplace, file_path, self.new_pairs_list)

    def bitstamp(self, marketplace, api_json):
        """Construct an ordered list of pairs for bitstamp marketplace
           then compare it.
           api_json : json, non ordered list from marketplace.
           return : list, ordered list of pairs from marketplace api.
        """
        btc_pairs = []
        eur_pairs = []
        usd_pairs = []
        all_pairs = []
        for obj in api_json:
            pair = obj['url_symbol']
            if pair[-3:] == 'btc':
                pair = marketplace.upper() + ':' + pair.upper()
                btc_pairs.append(pair)
                continue
            if pair[-3:] == 'eur':
                pair = marketplace.upper() + ':' + pair.upper()
                eur_pairs.append(pair)
                continue
            if pair[-3:] == 'usd':
                pair = marketplace.upper() + ':' + pair.upper()
                usd_pairs.append(pair)
                continue
        btc_pairs.sort()
        eur_pairs.sort()
        usd_pairs.sort()
        all_pairs = usd_pairs + btc_pairs + eur_pairs
        #return all_pairs # I wasn't able to return data from exec in main, need to be solved
        self.new_pairs_list = all_pairs

    def okcoin(self, marketplace, api_json):
        """Construct an ordered list of pairs for okcoin marketplace
           then compare it.
           api_json : json, non ordered list from marketplace.
           return : list, ordered list of pairs from marketplace api.
        """
        btc_pairs = []
        eth_pairs = []
        usd_pairs = []
        all_pairs = []
        for obj in api_json:
            pair = obj['instrument_id']
            if pair[-3:] == 'BTC':
                pair = marketplace.upper() + ':' + pair.replace('-', '')
                btc_pairs.append(pair)
                continue
            if pair[-3:] == 'ETH':
                pair = marketplace.upper() + ':' + pair.replace('-', '')
                eth_pairs.append(pair)
                continue
            if pair[-3:] == 'USD':
                pair = marketplace.upper() + ':' + pair.replace('-', '')
                usd_pairs.append(pair)
                continue
        btc_pairs.sort()
        eth_pairs.sort()
        usd_pairs.sort()
        all_pairs = usd_pairs + btc_pairs + eth_pairs
        #return all_pairs # I wasn't able to return data from exec in main, need to be solved
        self.new_pairs_list = all_pairs

    def coinbase(self, marketplace, api_json):
        """Construct an ordered list of pairs for coinbase marketplace
           then compare it.
           api_json : json, non ordered list from marketplace.
           return : list, ordered list of pairs from marketplace api.
        """
        btc_pairs = []
        eur_pairs = []
        gbp_pairs = []
        usd_pairs = []
        usdc_pairs = []
        all_pairs = []
        for obj in api_json:
            pair = obj['id']
            if pair[-3:] == 'BTC':
                pair = marketplace.upper() + ':' + pair.replace('-', '')
                btc_pairs.append(pair)
                continue
            if pair[-3:] == 'EUR':
                pair = marketplace.upper() + ':' + pair.replace('-', '')
                eur_pairs.append(pair)
                continue
            if pair[-3:] == 'GBP':
                pair = marketplace.upper() + ':' + pair.replace('-', '')
                gbp_pairs.append(pair)
                continue
            if pair[-4:] == 'USDC':
                pair = marketplace.upper() + ':' + pair.replace('-', '')
                usdc_pairs.append(pair)
                continue
            if pair[-3:] == 'USD':
                pair = marketplace.upper() + ':' + pair.replace('-', '')
                usd_pairs.append(pair)
                continue
        btc_pairs.sort()
        eur_pairs.sort()
        gbp_pairs.sort()
        usd_pairs.sort()
        usdc_pairs.sort()
        all_pairs = usd_pairs + eur_pairs + gbp_pairs + usdc_pairs + btc_pairs
        #return all_pairs # I wasn't able to return data from exec in main, need to be solved
        self.new_pairs_list = all_pairs

    def bitmex(self, marketplace, api_json):
        """Construct an ordered list of pairs for bitmex marketplace
           then compare it.
           api_json : json, non ordered list from marketplace.
           return : list, ordered list of pairs from marketplace api.
        """
        all_pairs = []
        for pair in api_json:
            pair = marketplace.upper() + ':' + pair['symbol']
            all_pairs.append(pair)
        all_pairs.sort()
        #return all_pairs # I wasn't able to return data from exec in main, need to be solved
        self.new_pairs_list = all_pairs

    def main(self):
        """Call every marketplace functions.
        """
        print("Lazy market list updater!")
        self.root_repository_failsafe()
        for marketplace in self.marketplace_obj:
            new_list = self.req_marketplace(marketplace)
            exec('self.' + marketplace + '(marketplace, new_list)')
            file_path = self.construct_file_path(marketplace)
            self.compare_pairs_list(marketplace, file_path, self.new_pairs_list)

        print("Job done.")

updater = market_lists_updater()

if __name__ == "__main__":
    updater.main()