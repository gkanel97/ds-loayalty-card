from dispatcher import Dispatcher
from user_interface import UserInterface
from failureSimulator import FailureSimulator

if __name__ == '__main__':
    # fs = FailureSimulator()
    # fs.concurrent_point_redemption()

    # user_interface = UserInterface(user_id='30d16d7b-592d-486d-a958-38d6fc921508', group_id=6)
    # print(user_interface.retrieve_group_points())
    # print(user_interface.redeem_points(5))
    # print(user_interface.register_purchase(10))
    # print(user_interface.retrieve_purchase_history())

    dispatcher = Dispatcher()
    dispatcher.try_saved_requests()