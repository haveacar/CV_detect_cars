import cv2
import os
from datetime import datetime
import psycopg2

class CarCount:
    def __init__(self, cascade):
        self.frame_counter = 0
        self.frame_date = datetime.min
        self.cascade = cascade

        # Database connection parameters
        self.db_name = '#'
        self.db_user = '#'
        self.db_pass = '#'
        self.db_host = '#'
        self.db_port = '#'

    def _load_car_cascade(self):
        """Load the Haar Cascade for car detection."""
        try:
            file_path = os.path.join(os.path.dirname(__file__), self.cascade)
            if not os.path.exists(file_path):
                raise FileNotFoundError("Haar cascade file not found.")

            car_cascade = cv2.CascadeClassifier(file_path)
            return car_cascade
        except Exception as e:
            print(f"Error loading Haar cascade: {e}")
            return None

    def _write_to_db(self, count:int, date, day):
        """Write detected car count to PostgreSQL database"""
        conn = None
        try:
            conn = psycopg2.connect(
                database=self.db_name,
                user=self.db_user,
                password=self.db_pass,
                host=self.db_host,
                port=self.db_port
            )

            # Open a cursor to perform database operations
            cur = conn.cursor()

            # Insert data
            query = "INSERT INTO car_statistics (day, date, count) VALUES (%s, %s, %s)"
            cur.execute(query, (day, date, count))

            # Commit the changes
            conn.commit()

            # Close the cursor and connection
            cur.close()

        except (Exception, psycopg2.DatabaseError) as error:
            print("Error while writing to PostgreSQL", error)
        finally:
            if conn is not None:
                conn.close()

    def _detect_cars(self, frame, car_cascade):
        """Convert frame to grayscale, detect cars only in the specified zone, and display the detection zone"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect cars
        cars = car_cascade.detectMultiScale(gray, 1.1, 2)

        # Define the detection zone dimensions
        height, width = frame.shape[:2]
        zone_width = int(width * 0.8)  # 80% of the frame's width

        # Calculate the starting x coordinate for the 80% width (centered)
        zone_x_start = width // 2 - zone_width // 2

        car_count = 0

        # Draw rectangles around detected cars in the specified zone
        for (x, y, w, h) in cars:
            # Check if the car is within the specified zone (full height, 80% width)
            if zone_x_start <= x <= zone_x_start + zone_width - w:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                car_count += 1

        # Display the detection zone on the frame
        cv2.rectangle(frame, (zone_x_start, 0), (zone_x_start + zone_width, height), (255, 0, 0), 2)

        # remove duplicate frames
        # if car_count > 0:
        #     time_now = datetime.now()
        #     if (time_now-self.frame_date).seconds >=3:
        #         self._write_to_db(1, time_now, time_now.weekday())
        #         self.frame_date = time_now


        return frame, car_count

    def generate_frames(self, url: str):
        """Generate frames to grayscale"""

        cap = cv2.VideoCapture(url)
        car_cascade = self._load_car_cascade()

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Detect cars in the frame
            frame_with_cars, car_count = self._detect_cars(frame, car_cascade)


            # Display the frame count and car count on the frame
            cv2.putText(frame_with_cars, f'Cars Count: {car_count}', (30, 750),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            # Display the frame
            cv2.imshow('Traffic Detection', frame)

            # Break the loop if 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()





