from computer_vision import CarCount
from controls import upload_configuration

def run():
    """Main Function"""
    # get config from settings file
    configuration = upload_configuration()

    car_count = CarCount(configuration.get('cascade_name'),
                         configuration.get('db_name'),
                         configuration.get('db_user'),
                         configuration.get('db_pass'),
                         configuration.get('db_host'),
                         )


    car_count.generate_frames(
        configuration.get('video_link'))


if __name__ == '__main__':
    run()