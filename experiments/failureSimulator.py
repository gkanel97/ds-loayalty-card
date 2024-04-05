import concurrent.futures
from user_interface import UserInterface

class FailureSimulator:
    def __init__(self):
        self.alice_ui = UserInterface(user_id='f09153ca-1c37-41f2-bde5-c4b20701ce6f', group_id=100)
        self.bob_ui = UserInterface(user_id='5416da69-ba03-4c58-aeb6-4ea7defe1d61', group_id=100)
        self.cynthia_ui = UserInterface(user_id='bc439a07-37cc-4ee7-9676-31646d440726', group_id=100)

    def read_points(self):
        alice_points = self.alice_ui.retrieve_group_points()['response']['total_points']
        bob_points = self.bob_ui.retrieve_group_points()['response']['total_points']
        cynthia_points = self.cynthia_ui.retrieve_group_points()['response']['total_points']
        print(f'Alice: {alice_points}, Bob: {bob_points}, Cynthia: {cynthia_points}')

    def verify_point_update(self):
        # Read points before update
        print('Before points update:')
        self.read_points()

        # Update points
        self.alice_ui.register_purchase(10)

        # Read points after update
        print('After points update:')
        self.read_points()

    def concurrent_point_update(self):
        # Read points before update
        print('Before points update:')
        self.read_points()

        # Update points concurrently
        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.submit(self.alice_ui.register_purchase, 10)
            executor.submit(self.bob_ui.register_purchase, 20)
            executor.submit(self.cynthia_ui.register_purchase, 30)

        # Read points after update
        print('After points update:')
        self.read_points()

    def concurrent_point_redemption(self):
        # Read points before redemption
        print('Before points redemption:')
        self.read_points()

        # Redeem points concurrently
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future1 = executor.submit(self.alice_ui.redeem_points, 35)
            future2 = executor.submit(self.bob_ui.redeem_points, 10)
            future3 = executor.submit(self.cynthia_ui.redeem_points, 35)

        print(f'Alice: {future1.result()}')
        print(f'Bob: {future2.result()}')
        print(f'Cynthia: {future3.result()}')

        # Read points after redemption
        print('After points redemption:')
        self.read_points()

