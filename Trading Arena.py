from collections import deque
import time
import random
from random import choice
from abc import ABC

from enum import Enum


class OrderType(Enum):
    LIMIT = 1
    MARKET = 2
    IOC = 3


class OrderSide(Enum):
    BUY = 1
    SELL = 2


class NonPositiveQuantity(Exception):
    pass


class NonPositivePrice(Exception):
    pass


class InvalidSide(Exception):
    pass


class UndefinedOrderType(Exception):
    pass


class UndefinedOrderSide(Exception):
    pass


class NewQuantityNotSmaller(Exception):
    pass


class UndefinedTraderAction(Exception):
    pass


class UndefinedResponse(Exception):
    pass


class Order(ABC):
    def __init__(self, id, symbol, quantity, side, time):
        self.id = id
        self.symbol = symbol
        if quantity > 0:
            self.quantity = quantity
        else:
            raise NonPositiveQuantity("Quantity Must Be Positive!")
        if side in [OrderSide.BUY, OrderSide.SELL]:
            self.side = side
        else:
            raise InvalidSide("Side Must Be Either \"Buy\" or \"OrderSide.SELL\"!")
        self.time = time


class LimitOrder(Order):
    def __init__(self, id, symbol, quantity, price, side, time):
        super().__init__(id, symbol, quantity, side, time)
        if price >= 0:
            self.price = price
        else:
            raise NonPositivePrice("Price Must Be Positive!")
        self.type = OrderType.LIMIT


class MarketOrder(Order):
    def __init__(self, id, symbol, quantity, side, time):
        super().__init__(id, symbol, quantity, side, time)
        self.type = OrderType.MARKET


class IOCOrder(Order):
    def __init__(self, id, symbol, quantity, price, side, time):
        super().__init__(id, symbol, quantity, side, time)
        if price > 0:
            self.price = price
        else:
            raise NonPositivePrice("Price Must Be Positive!")
        self.type = OrderType.IOC


class FilledOrder(Order):
    def __init__(self, id, symbol, quantity, price, side, time, limit=False):
        super().__init__(id, symbol, quantity, side, time)
        self.price = price
        self.limit = limit


trader_to_exchange = deque()
exchange_to_trader = [deque() for _ in range(100)]


class MissingParams(Exception):
    pass


# Above you are given two deques where the orders submitted to the exchange and back to the trader
# are expected to be populated by the trading exchange simulator
# The first is trader_to_exchange, a deque of orders to be populated for the exchange to execute
# The second is a list of 100 deques exchange_to_trader, which are acknowledgements from the exchange
# to each of the 100 traders for trades executed on their behalf

# Below you have an implementation of a simulated thread to be used where each trader is a separate thread

class MyThread:
    list_of_threads = []

    def __init__(self, id='NoID'):
        MyThread.list_of_threads.append(self)
        self.is_started = False
        self.id = id

    def start(self):
        self.is_started = True

    def join(self):
        print('Trader ' + str(self.id) + ' will be waited')


# Paste in your implementation for the matching engine below

# ----------------------------------------------------------
class MatchingEngine():

    def __init__(self):
        self.bid_book = []  # price from high to low / buy, then sorted by the time
        self.ask_book = []  # price from low to high / sell, then sorted by the time
        # These are the order books you are given and expected to use for matching the orders below

    # Note: As you implement the following functions keep in mind that these enums are available:
    #     class OrderType(Enum):
    #         LIMIT = 1
    #         MARKET = 2
    #         IOC = 3
    #     class OrderSide(Enum):
    #         BUY = 1
    #         SELL = 2

    def handle_order(self, order):
        # Implement this function
        # In this function you need to call different functions from the matching engine
        # depending on the type of order you are given
        if order.type == OrderType.LIMIT:
            self.handle_limit_order(order)
        elif order.type == OrderType.MARKET:
            self.handle_market_order(order)
        elif order.type == OrderType.IOC:
            self.handle_ioc_order(order)
        else:
            raise UndefinedOrderType("Undefined Order Type!")


    def handle_limit_order(self, order):
        filled_orders = []
        # The orders that are filled from the market order need to be inserted into the above list
        total_quantity = order.quantity
        if order.side == OrderSide.BUY:
            order_fully_traded = False
            if len(self.ask_book) != 0:
                for ask_order in self.ask_book:
                    if (ask_order.type == OrderType.LIMIT and ask_order.price >= order.price) or ask_order.type == OrderType.MARKET:
                        # then those two limit orders / a limit and a market could be traded
                        if ask_order.quantity < order.quantity:
                            order.quantity -= ask_order.quantity
                            filled_order = FilledOrder(ask_order.id, ask_order.symbol, ask_order.quantity,
                                                       ask_order.price if ask_order.type == OrderType.LIMIT else order.price,
                                                       OrderSide.BUY, ask_order.time,
                                                       True if ask_order.type == 1 else False)
                            filled_orders.append(filled_order)
                        elif ask_order.quantity > order.quantity:  # matching is complete
                            ask_order.quantity -= order.quantity
                            order_fully_traded = True
                            filled_order = FilledOrder(order.id, order.symbol, total_quantity, order.price,
                                                       OrderSide.BUY, order.time,
                                                       True)  # the trade price is order.price?
                            filled_order_2 = FilledOrder(ask_order.id, ask_order.symbol, order.quantity,
                                                         ask_order.price if ask_order.type == OrderType.LIMIT else order.price,
                                                         OrderSide.SELL, ask_order.time,
                                                         True if ask_order.type == OrderType.LIMIT else False)
                            filled_orders.append(filled_order)
                            filled_orders.append(filled_order_2)
                            break
                        else:
                            order_fully_traded == True
                            filled_order_1 = FilledOrder(order.id, order.symbol, total_quantity, ask_order.price,
                                                         OrderSide.BUY, order.time, True)
                            filled_order_2 = FilledOrder(ask_order.id, ask_order.symbol, ask_order.quantity,
                                                         ask_order.price if ask_order.type == OrderType.MARKET else order.price,
                                                         OrderSide.SELL, ask_order.time,
                                                         True if ask_order.type == OrderType.LIMIT else False)
                            filled_orders.append(filled_order_1, filled_order_2)
                            break

                self.ask_book = self.ask_book[len(filled_orders) - 2:]  # to update the current self.ask_book
                # after the for loop, if the order still is not fully traded, then insert the remaining
                if order_fully_traded == False:
                    self.insert_limit_order(order)
                    if order.quantity < total_quantity:
                        filled_order = FilledOrder(order.id, order.symbol, total_quantity - order.quantity, order.price,
                                                   OrderSide.SELL, order.time, True)
                        filled_orders.append(filled_order)
            else:
                self.insert_limit_order(order)

        elif order.side == OrderSide.SELL:
            order_fully_traded = False
            if len(self.bid_book) != 0:
                for bid_order in self.bid_book:
                    if (bid_order.type == OrderType.LIMIT and bid_order.price > order.price) or bid_order.type == OrderType.MARKET:
                        # then the trade is between two limited orders / a limited order and a market order
                        if bid_order.quantity < order.quantity:
                            order.quantity -= bid_order.quantity;
                            filled_order = FilledOrder(bid_order.id, bid_order.symbol, bid_order.quantity,
                                                       bid_order.price, OrderSide.BUY, bid_order.time,
                                                       True if bid_order.type == OrderType.LIMIT else False)
                            filled_orders.append(filled_order)

                        elif bid_order.quantity > order.quantity:  # the order is filled
                            bid_order.quantity -= order.quantity
                            order_fully_traded = True
                            filled_order_1 = FilledOrder(order.id, bid_order.symbol, total_quantity, order.price,
                                                         OrderSide.SELL, order.time, True)
                            filled_order_2 = FilledOrder(bid_order.id, bid_order.symbol, order.quantity,
                                                         bid_order.price, OrderSide.BUY, bid_order.time,
                                                         True if bid_order.type == OrderType.LIMIT else False)
                            filled_orders.append(filled_order_1)
                            filled_orders.append(filled_order_2)
                            break
                        else:
                            order_fully_traded == True
                            filled_order_1 = FilledOrder(order.id, order.symbol, total_quantity, order.price,
                                                         OrderSide.SELL, order.time, True)
                            filled_order_2 = FilledOrder(bid_order.id, bid_order.symbol, bid_order.quantity,
                                                         bid_order.price if bid_order.type == OrderType.MARKET else order.price,
                                                         OrderSide.BUY, bid_order.time,
                                                         True if bid_order.type == OrderType.LIMIT else False)
                            filled_orders.append(filled_order_1)
                            filled_orders.append(filled_order_2)
                            break

                self.bid_book = self.bid_book[len(filled_orders) - 2:]  # to update the order book
                if order_fully_traded == False:
                    self.insert_limit_order(order)
                    if order.quantity < total_quantity:
                        filled_order = FilledOrder(order.id, order.symbol, total_quantity - order.quantity, order.price,
                                                   OrderSide.SELL, order.time, True)
                        filled_orders.append(filled_order)
            else:
                self.insert_limit_order(order)
        else:
            # You need to raise the following error if the side the order is for is ambiguous
            raise UndefinedOrderSide("Undefined Order Side!")
        return filled_orders

    def handle_market_order(self, order):
        # Implement this function
        filled_orders = []
        total_quantity = order.quantity
        if order.side == OrderSide.BUY:  # buy, then go to check the self.ask_book, and take whatever the price is
            if len(self.ask_book) != 0:  # there're still some orders
                total_quantity = order.quantity

                for ask_order in self.ask_book:
                    if ask_order.quantity < order.quantity:
                        order.quantity -= ask_order.quantity  # the remaining quantity to be traded
                        traded_order = FilledOrder(ask_order.id, ask_order.symbol, ask_order.quantity,
                                                   0 if ask_order.type == OrderType.MARKET else ask_order.price,
                                                   OrderSide.SELL, ask_order.time,
                                                   False if ask_order.type == OrderType.MARKET else True)
                        filled_orders.append(traded_order)

                    elif ask_order.quantity > order.quantity:  # order.quantity now will be zero, the order is fully traded
                        ask_order.quantity -= order.quantity
                        filled_order_1 = FilledOrder(order.id, order.symbol, total_quantity, ask_order.price,
                                                     OrderSide.BUY,
                                                     order.time, False)
                        filled_order_2 = FilledOrder(ask_order.id, ask_order.symbol, order.quantity, ask_order.price,
                                                     OrderSide.SELL, ask_order.time, False)
                        filled_orders.append(filled_order_1)
                        filled_orders.append(filled_order_2)
                        self.ask_book = self.ask_book[len(filled_orders) - 2:]
                        break

                    else:
                        filled_order_1 = FilledOrder(ask_order.id, ask_order.symbol, ask_order.quantity,
                                                     0 if ask_order.type == OrderType.MARKET else ask_order.price,
                                                     OrderSide.SELL, ask_order.time,
                                                     False if ask_order.type == OrderType.MARKET else True)
                        filled_order_2 = FilledOrder(order.id, order.symbol, total_quantity,
                                                     0 if ask_order.type == OrderType.MARKET else ask_order.price,
                                                     OrderSide.BUY, order.time,
                                                     False)
                        filled_orders.append(filled_order_1, filled_order_2)
                        self.ask_book = self.ask_book[len(filled_orders):]
                        break
            else:  # the ask book is empty
                self.bid_book.append(order)
                filled_order = FilledOrder(order.id, order.symbol, total_quantity - order.quantity, 0,
                                           OrderSide.BUY, order.time, False)
                filled_orders.append(filled_order)

        elif order.side == OrderSide.SELL:  # now the order is to sell
            if len(self.bid_book) != 0:
                total_quantity = order.quantity
                for bid_order in self.bid_book:
                    if bid_order.quantity < order.quantity:
                        order.quantity -= bid_order.quantity  # the remaining quantity to be traded
                        traded_order = FilledOrder(bid_order.id, bid_order.symbol, bid_order.quantity,
                                                   0 if bid_order.type == OrderType.MARKET else bid_order.price,
                                                   OrderSide.BUY, bid_order.time,
                                                   False if bid_order.type == OrderType.MARKET else True)
                        filled_orders.append(traded_order)

                    elif bid_order.quantity > order.quantity:  # order.quantity now will be zero, the order is fully traded
                        bid_order.quantity -= order.quantity
                        filled_order_1 = FilledOrder(order.id, order.symbol, total_quantity, bid_order.price,
                                                     OrderSide.SELL,
                                                     order.time, False)
                        filled_order_2 = FilledOrder(bid_order.id, bid_order.symbol, order.quantity,
                                                     bid_order.price if bid_order.type == OrderType.LIMIT else 0,
                                                     OrderSide.BUY, bid_order.time,
                                                     True if bid_order.type == OrderType.LIMIT else False)
                        filled_orders.append(filled_order_1)
                        filled_orders.append(filled_order_2)
                        self.bid_book = self.bid_book[len(filled_orders) - 2:]
                        break
                    else:
                        filled_order_1 = FilledOrder(bid_order.id, bid_order.symbol, bid_order.quantity,
                                                     0 if bid_order.type == OrderType.MARKET else bid_order.price,
                                                     OrderSide.BUY, bid_order.time,
                                                     False if bid_order.type == OrderType.MARKET else True)
                        filled_order_2 = FilledOrder(order.id, order.symbol, total_quantity,
                                                     0 if bid_order.type == OrderType.MARKET else bid_order.price,
                                                     OrderSide.SELL, order.time,
                                                     False)
                        filled_orders.append(filled_order_1)
                        filled_orders.append(filled_order_2)
            else:  # the ask book is empty
                self.ask_book.append(order)
                filled_order = FilledOrder(order.id, order.symbol, total_quantity - order.quantity, 0,
                                           OrderSide.SELL, order.time, False)
                filled_orders.append(filled_order)

        # The orders that are filled from the market order need to be inserted into the above list
        else:
            raise UndefinedOrderSide("Undefined Order Side!")

        return filled_orders

    def handle_ioc_order(self, order):

        filled_orders = []
        # The orders that are filled from the ioc order need to be inserted into the above list
        if order.side == OrderSide.BUY:  # to check the existing sell order book
            if len(self.ask_book)>0:
                order_traded = self.ask_book[0]  # The IOC should trade with any existing order
                if (order_traded.type == 2) or (
                        order_traded.type == 1 and order.price >= order_traded.price):  # market order, trade price will equal to IOC
                    traded_quantity = min(order.quantity, order_traded.quantity)
                    if traded_quantity == order_traded.quantity:  # the first order is fully traded
                        self.ask_book = self.ask_book[1:]
                        filled_order_1 = FilledOrder(order_traded.id, order_traded.symbol, traded_quantity, order.price,
                                                     2, order_traded.time, False if order_traded.type == 2 else True)
                        filled_IOC = FilledOrder(order.id, order.symbol, traded_quantity, order.price, 1, order.time,
                                                 False)
                        filled_orders.append(filled_order_1)
                        filled_orders.append(filled_IOC)  # IOC order
                    else:  # the first order is partially traded, will update its remaining quantity
                        filled_IOC = FilledOrder(order.id, order.symbol, traded_quantity, order.price, 1, order.time,
                                                 False)
                        order_traded.quantity -= traded_quantity
                        filled_orders.append(filled_IOC)  # IOC order

        elif order.side == OrderSide.SELL:  # it's a sell order, to check the self buy order book
            if len(self.bid_book)>0:
                order_traded = self.bid_book[0]
                if (order_traded.type == OrderType.MARKET) or (
                        order_traded.type == OrderType.LIMIT and order.price < order_traded.price):
                    traded_quantity = min(order.quantity, order_traded.quantity)
                    if traded_quantity == order_traded.quantity:  # the first order is fully traded
                        self.bid_book = self.bid_book[1:]
                        filled_order_1 = FilledOrder(order_traded.id, order_traded.symbol, traded_quantity, order.price,
                                                     OrderSide.BUY, order_traded.time,
                                                     False if order_traded.type == OrderType.MARKET else True)
                        filled_IOC = FilledOrder(order.id, order.symbol, traded_quantity, order.price, 2, order.time,
                                                 False)
                        filled_orders.append(filled_order_1)
                        filled_orders.append(filled_IOC)  # IOC order
                    else:  # the first order is partially traded, will update its remaining quantity
                        filled_IOC = FilledOrder(order.id, order.symbol, traded_quantity, order.price, OrderSide.SELL,
                                                 order.time,
                                                 False)
                        order_traded.quantity -= traded_quantity
                        filled_orders.append(filled_IOC)  # IOC order
        else:
            raise UndefinedOrderSide("Undefined Order Side!")
        return filled_orders

    def insert_limit_order(self, order):
        assert order.type == OrderType.LIMIT
        list_of_bids = []
        list_of_offrs = []

        if order.side == OrderSide.BUY:  # BUY Order
            list_of_bids.append(order)
            self.bid_book += list_of_bids
            self.bid_book = sorted(self.bid_book, key=lambda x: (x.price, -x.time), reverse=True)

        elif order.side == OrderSide.SELL:
            list_of_offrs.append(order)
            self.ask_book += list_of_offrs
            self.ask_book = sorted(self.ask_book, key=lambda x: (x.price, -x.time))
        else:
            raise UndefinedOrderSide("Undefined Order Side!")

    def amend_quantity(self, id, quantity):

        for order in self.bid_book:
            if order.id == id:
                if order.quantity > quantity:
                    order.quantity = quantity
                    return True
                else:
                    raise NewQuantityNotSmaller("Amendment Must Reduce Quantity!")
        for order in self.ask_book:
            if order.id == id:
                if order.quantity > quantity:
                    order.quantity = quantity
                    return True
                else:
                    raise NewQuantityNotSmaller("Amendment Must Reduce Quantity!")
        return False

    def cancel_order(self, id):
        for order in self.bid_book:
            if order.id == id:
                self.bid_book.remove(order)
                return True
        for order in self.ask_book:
            if order.id == id:
                self.ask_book.remove(order)
                return True
        return False

# -----------------------------------------------------------

# Each trader can take a separate action chosen from the list below:

# Actions:
# 1 - Place New Order/Order Filled
# 2 - Amend Quantity Of An Existing Order
# 3 - Cancel An Existing Order
# 4 - Return Balance And Position

# request - (Action #, Trader ID, Additional Arguments)

# result - (Action #, Action Return)

# WE ASSUME 'AAPL' IS THE ONLY TRADED STOCK.

class OrderActions(Enum):
    Place = 1
    Amend = 2
    Cancel = 3
    Return_Balance_And_Position = 4


class Trader(MyThread):
    def __init__(self, id):
        super().__init__(id)
        self.book_position = 0
        self.balance_track = [1000000] # a track?
        # the traders each start with a balance of 1,000,000 and nothing on the books
        # each trader is a thread

        # Make sure the limit order given has the parameters necessary to construct the order
        # It's your choice how to implement the orders that do not have enough information
        # The 'order' returned must be of type LimitOrder
        # Make sure you modify the book position after the trade
        # You must return a tuple of the following:
        # (the action type enum, the id of the trader, and the order to be executed)

    def place_limit_order(self, quantity=None, price=None, side=None):
        new_order = LimitOrder(self.id, symbol='AAPL', quantity=quantity, price=price, side=side, time=time.time())
        if new_order.quantity == None:
            raise MissingParams('Undefined Quantity!')
        if new_order.price == None:
            raise MissingParams('Undefined Price!')
        if new_order.side == None:
            raise MissingParams('Undefined Side!')

        trader_to_exchange.append((OrderType.LIMIT, new_order.id, new_order))

    def place_market_order(self, quantity=None, side=None):

        market_order = MarketOrder(self.id, 'AAPL', quantity, side, time=time.time())

        if market_order.quantity == None:
            raise MissingParams('Undefined Quantity!')
        if market_order.side == None:
            raise MissingParams('Undefined Side!')

        trader_to_exchange.append((OrderType.MARKET, market_order.id, market_order))

    def place_ioc_order(self, quantity=None, price=None, side=None):

        ioc_order = IOCOrder(self.id, 'AAPL', quantity, price, side, time=time.time())
        if ioc_order.quantity == None:
            raise MissingParams('Undefined Quantity!')
        if ioc_order.price == None:
            raise MissingParams('Undefined Price!')
        if ioc_order.side == None:
            raise MissingParams('Undefined Side!')

        trader_to_exchange.append((ioc_order.type, ioc_order.id, ioc_order))

    def amend_quantity(self, quantity=None):
        # It's your choice how to implement the 'Amend' action where quantity is not given
        if quantity == None:
            raise MissingParams('The Quantity is not given!')
        # (the action type enum, the id of the trader, and quantity to change the order by)
        trader_to_exchange.append((OrderActions.Amend, self.id, quantity))

    def cancel_order(self):
        trader_to_exchange.append((OrderActions.Cancel,self.id))

    def balance_and_position(self):
        trader_to_exchange.append((OrderActions.Return_Balance_And_Position,self.id))

    def process_response(self, response):
        # Implement this function
        # the response could be in the following formats
        # 1. (OrderActions.Place,order) from Exchange.place_new_order()
        # 2. (OrderActions.Amend, result) from Exchange.amend_quantity()
        # 3. (OrderActions.Cancel,result) from Exchange.cancel_order()
        # 4. (OrderActions.Return_Balance_And_Position,(self.balance[id], self.position[id])) from Exchange.return_cash_and_position()

        if response[0] == OrderActions.Amend and response[1] == True:
            print('Order Quantity Amendment Successful!')
        elif response[0] == OrderActions.Cancel and response[1] == True:
            print('Order Cancellation Successful!')
        elif response[0] == OrderActions.Return_Balance_And_Position and response[1] == True:
            print('The balance is:',response[1][0], ', The position is:',response[1][1])
        elif response[0] == OrderActions.Place:
            if response[1].side == OrderSide.BUY:
                self.book_position += response[1].quantity
                self.balance_track.append(self.balance_track[-1] - (response[1].price * response[1].quantity) - 1000000)
            else:
                self.book_position -= response[1].quantity
                self.balance_track.append(self.balance_track[-1] + (response[1].price * response[1].quantity) - 1000000)
        else:
            raise UndefinedResponse("Undefined Response Received!")

    def random_action(self):

        if self.book_position == 0:
            self.place_limit_order(10,5,OrderSide.BUY)

        action_list = [1,2,3,4]
        result = choice(action_list)
        if result == 1:
            self.place_limit_order(10,10,OrderSide.BUY) # a sample order
        elif result == 2:
            self.balance_and_position()
        elif result == 3:
            self.cancel_order()
        else:
            self.place_limit_order(10,1,OrderSide.SELL)

    # Implement this function
    # According to the status of whether you have a position on the book and the action chosen
    # the trader needs to be able to take a separate action
    # The action taken can be random or deterministic, your choice

    def run_infinite_loop(self):

        while exchange_to_trader[self.id]:
            response = exchange_to_trader[self.id].popleft()
            if response:
                self.process_response(response)

        while self.balance_track[-1] > 0:
            print(self.balance_track)
            self.random_action()
            while exchange_to_trader[self.id]:
                response = exchange_to_trader[self.id].popleft()
                if response:
                    self.process_response(response)
            break


# The trader needs to continue to take actions until the book balance falls to 0
# While the trader can take actions, it chooses from a random_action and uploads the action
# to the exchange
# The trader then takes any received responses from the exchange and processes it

class Exchange(MyThread):
    def __init__(self):
        super().__init__()
        self.balance = [1000000 for _ in range(100)]
        self.position = [0 for _ in range(100)]
        self.matching_engine = MatchingEngine()
        # The exchange keeps track of the traders' balances

    def place_new_order(self, order):
        # The exchange must use the matching engine to handle orders given
        results = []
        filled = self.matching_engine.handle_order(order)
        if filled:
            for filled_order in filled:
                filled_quant = filled_order.quantity
                money_changed = filled_quant * filled_order.price if filled_order.side == OrderSide.SELL else filled_quant * (-filled_order.price)
                self.balance[filled_order.id] += money_changed
                self.position[filled_order.id] = self.position[filled_order.id]+filled_quant if filled_order.side == OrderSide.BUY else self.position[filled_order.id]-filled_quant
                output = (filled_order.id, (OrderActions.Place, filled_order))
                results.append(output)

        # The list of results is expected to contain a tuple of the follow form:
        # (Trader id that processed the order, (action type enum, order))
        # The exchange must update the balance of positions of each trader involved in the trade (if any)
        return results

    def amend_quantity(self, id, quantity):

        result = self.matching_engine.amend_quantity(id, quantity)
        return (OrderActions.Amend, result)
        # The matching engine must be able to process the 'amend' action based on the given parameters
        # Keep in mind of any exceptions that may be thrown by the matching engine while handling orders
        # The return must be in the form (action type enum, logical based on if order processed)

    def cancel_order(self, id):

        result = self.matching_engine.cancel_order(id)
        return (OrderActions.Cancel,result)

    def balance_and_position(self, id):

        return (OrderActions.Return_Balance_And_Position,(self.balance[id], self.position[id]))
        # The matching engine must be able to process the 'balance' action based on the given parameters
        # The return must be in the form (action type enum, (trader balance, trader positions))

    def handle_request(self, request):
        # The exchange must be able to process different types of requests based on the action
        # type given using the functions implemented above
        if request[0] == OrderType.MARKET or request[0] == OrderType.LIMIT or request[0] == OrderType.IOC:
            self.place_new_order(request[2])
        elif request[0] == OrderActions.Amend:
            self.amend_quantity(request[1],request[2])
        elif request[0] == OrderActions.Cancel:
            self.cancel_order(request[1])
        elif request[0] == OrderActions.Return_Balance_And_Position:
            self.balance_and_position(request[1])
        else:
            raise UndefinedTraderAction("Undefined Trader Action!")

    def run_infinite_loop(self):
        while trader_to_exchange:
            request = trader_to_exchange.popleft()

            if request:
                response = self.handle_request(request)
                #print(type(response))

            if isinstance(response,list):
                for order in response:
                    exchange_to_trader[order[0]].append(order[1])
            else:
                exchange_to_trader[request[1]].append(response)
# The exchange must continue handling orders as orders are issued by the traders
# A way to do this is check if there are any orders waiting to be processed in the deque

# If there are, handle the request using the functions built above and using the
# corresponding trader's deque, return an acknowledgement based on the response

if __name__ == "__main__":

    trader = [Trader(i) for i in range(100)]
    exchange = Exchange()

    exchange.start()
    for t in trader:
        t.start()

    exchange.join()
    for t in trader:
        t.join()

    sum_exch = 0
    for t in MyThread.list_of_threads:
        if t.id == "NoID":
            for b in t.balance:
                sum_exch += b

    print("Total Money Amount for All Traders before Trading Session: " + str(sum_exch))

    for i in range(10000):
        thread_active = False
        for t in MyThread.list_of_threads:
            if t.is_started:
                t.run_infinite_loop()
                thread_active = True
        if not thread_active:
            break

    sum_exch = 0
    for t in MyThread.list_of_threads:
        if t.id == "NoID":
            for b in t.balance:
                sum_exch += b

    print("Total Money Amount for All Traders after Trading Session: ", str(int(sum_exch)))
