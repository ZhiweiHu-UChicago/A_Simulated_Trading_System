import time

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


from abc import ABC


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
        if price > 0:
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

        # The orders that are filled from the market order need to be inserted into the above list
        else:
            raise UndefinedOrderSide("Undefined Order Side!")

        return filled_orders

    def handle_ioc_order(self, order):

        filled_orders = []
        # The orders that are filled from the ioc order need to be inserted into the above list
        if order.side == OrderSide.BUY:  # to check the existing sell order book
            if len(self.ask_book) > 0:
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
            if len(self.bid_book) > 0:
                order_traded = self.bid_book[0]
                if (order_traded.type == OrderType.MARKET) or (
                        order_traded.type == OrderType.LIMIT and order.price < order_traded.price):
                    traded_quantity = min(order.quantity, order_traded.quantity)
                    if traded_quantity == order_traded.quantity:  # the first order is fully traded
                        self.bid_book = self.bid_book[1:]
                        filled_order_1 = FilledOrder(order_traded.id, order_traded.symbol, traded_quantity, order.price,
                                                     OrderSide.BUY, order_traded.time,
                                                     False if order_traded.type == OrderType.MARKET else True)
                        filled_IOC = FilledOrder(order.id, order.symbol, traded_quantity, order.price,OrderSide.SELL, order.time,
                                                 False)
                        filled_orders.append(filled_order_1)
                        filled_orders.append(filled_IOC)  # IOC order
                    else:  # the first order is partially traded, will update its remaining quantity
                        filled_order_1 = FilledOrder(order_traded.id, order_traded.symbol, traded_quantity, order.price,
                                                     OrderSide.BUY, order_traded.time,
                                                     False if order_traded.type == OrderType.MARKET else True)
                        filled_IOC = FilledOrder(order.id, order.symbol, traded_quantity, order.price, OrderSide.SELL,
                                                 order.time,
                                                 False)
                        order_traded.quantity -= traded_quantity
                        filled_orders.append(filled_order_1)
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
# You need to build additional unittests for your implementation
import unittest


class TestOrderBook(unittest.TestCase):

    # The unittests must start with "test", change the function name to something that makes sense
    def test_handle_Market_order(self):
        # implement this unittest and three more
        matching_engine = MatchingEngine()
        order = MarketOrder(1, 'S', 10, OrderSide.BUY, time.time())
        matching_engine.handle_market_order(order)

        self.assertEqual(matching_engine.bid_book[0].quantity,10)
        self.assertEqual(matching_engine.bid_book[0].symbol,'S')

        order_2 = MarketOrder(2,' S', 10, OrderSide.SELL, time.time())
        filled_order = matching_engine.handle_market_order(order_2)
        self.assertEqual(filled_order[0].price,0)

    def test_handle_IOC_order(self):
        matching_engine = MatchingEngine()
        order = IOCOrder(1,'S',10,10,OrderSide.SELL,time.time())
        order_2 = MarketOrder(2,'S',10,OrderSide.BUY,time.time())

        matching_engine.handle_market_order(order_2)
        filled_order = matching_engine.handle_ioc_order(order)
        self.assertEqual(filled_order[0].quantity,10)
        self.assertEqual(filled_order[1].price,10)

    def test_amend_quantity_1(self):
        matching_engine = MatchingEngine()
        order_1 = MarketOrder(1,'S',10,OrderSide.SELL,time.time())
        matching_engine.handle_market_order(order_1)
        matching_engine.amend_quantity(1,8)

        self.assertEqual(matching_engine.ask_book[0].quantity,8)

    def test_cancel_order_1(self):
        matching_engine = MatchingEngine()
        order_1 = LimitOrder(1,'S',10,10,OrderSide.BUY,time.time())
        matching_engine.handle_limit_order(order_1)
        matching_engine.cancel_order(1)

        self.assertEqual(len(matching_engine.bid_book),0)

    # A few example unittests are provided below

    def test_insert_limit_order(self):
        matching_engine = MatchingEngine()
        order = LimitOrder(1, "S", 10, 10, OrderSide.BUY, time.time())
        matching_engine.insert_limit_order(order)

        self.assertEqual(matching_engine.bid_book[0].quantity, 10)
        self.assertEqual(matching_engine.bid_book[0].price, 10)

    def test_handle_limit_order(self):
        matching_engine = MatchingEngine()
        order = LimitOrder(1, "S", 10, 10, OrderSide.BUY, time.time())
        matching_engine.insert_limit_order(order)

        order_1 = LimitOrder(2, "S", 5, 10, OrderSide.BUY, time.time())
        order_2 = LimitOrder(3, "S", 10, 15, OrderSide.BUY, time.time())
        matching_engine.handle_limit_order(order_1)
        matching_engine.handle_limit_order(order_2)

        self.assertEqual(matching_engine.bid_book[0].price, 15)
        self.assertEqual(matching_engine.bid_book[1].quantity, 10)

        order_sell = LimitOrder(4, "S", 14, 8, OrderSide.SELL, time.time())
        filled_orders = matching_engine.handle_limit_order(order_sell)

        self.assertEqual(matching_engine.bid_book[0].quantity, 6)
        self.assertEqual(filled_orders[0].id, 3)
        self.assertEqual(filled_orders[0].price, 15)
        self.assertEqual(filled_orders[2].id, 1)
        self.assertEqual(filled_orders[2].price, 10)

    def test_handle_market_order(self):
        matching_engine = MatchingEngine()
        order_1 = LimitOrder(1, "S", 6, 10, OrderSide.BUY, time.time())
        order_2 = LimitOrder(2, "S", 5, 10, OrderSide.BUY, time.time())
        matching_engine.handle_limit_order(order_1)
        matching_engine.handle_limit_order(order_2)

        order = MarketOrder(5, "S", 5, OrderSide.SELL, time.time())
        filled_orders = matching_engine.handle_market_order(order)
        self.assertEqual(matching_engine.bid_book[0].quantity, 1)
        self.assertEqual(filled_orders[0].price, 10)

    def test_handle_ioc_order(self):
        matching_engine = MatchingEngine()
        order_1 = LimitOrder(1, "S", 1, 10, OrderSide.BUY, time.time())
        order_2 = LimitOrder(2, "S", 5, 10, OrderSide.BUY, time.time())
        matching_engine.handle_limit_order(order_1)
        matching_engine.handle_limit_order(order_2)

        order = IOCOrder(6, "S", 5, 12, OrderSide.SELL, time.time())
        filled_orders = matching_engine.handle_ioc_order(order)
        self.assertEqual(matching_engine.bid_book[0].quantity, 1)
        self.assertEqual(len(filled_orders), 0)

    def test_amend_quantity(self):
        matching_engine = MatchingEngine()
        order_1 = LimitOrder(1, "S", 5, 10, OrderSide.BUY, time.time())
        order_2 = LimitOrder(2, "S", 10, 15, OrderSide.BUY, time.time())
        matching_engine.handle_limit_order(order_1)
        matching_engine.handle_limit_order(order_2)

        matching_engine.amend_quantity(2, 8)
        self.assertEqual(matching_engine.bid_book[0].quantity, 8)

    def test_cancel_order(self):
        matching_engine = MatchingEngine()
        order_1 = LimitOrder(1, "S", 5, 10, OrderSide.BUY, time.time())
        order_2 = LimitOrder(2, "S", 10, 15, OrderSide.BUY, time.time())
        matching_engine.handle_limit_order(order_1)
        matching_engine.handle_limit_order(order_2)

        matching_engine.cancel_order(1)
        self.assertEqual(matching_engine.bid_book[0].id, 2)


import io
import __main__

suite = unittest.TestLoader().loadTestsFromModule(__main__)
buf = io.StringIO()
unittest.TextTestRunner(stream=buf, verbosity=2).run(suite)
buf = buf.getvalue().split("\n")
sum = 0
for test in buf:
    if test.startswith("test"):
        sum += 1

print("You have %d unit tests" % (sum))

