import cv2
import os
from datetime import datetime
import psycopg2


class CarCount:
    def __init__(self, cascade, db_name, db_user, db_pass, db_host, db_port=5432):
        self.frame_counter = 0
        self.frame_date = datetime.min
        self.cascade = cascade

        # Database connection parameters
        self.db_name = db_name
        self.db_user = db_user
        self.db_pass = db_pass
        self.db_host = db_host
        self.db_port = db_port

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

    def _write_to_db(self, count: int, date, day):
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
        """Updated method to adjust detection zone and handle frame duplication"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        cars = car_cascade.detectMultiScale(gray, 1.1, 3)

        # calculate detection zone
        height, width = frame.shape[:2]
        zone_width = int(width * 0.8)
        zone_height_start = int(height * 0.08)
        zone_height_end = height
        zone_x_start = width // 2 - zone_width // 2

        car_count = 0
        for (x, y, w, h) in cars:
            if zone_x_start <= x <= zone_x_start + zone_width - w and zone_height_start <= y <= zone_height_end - h:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                car_count += 1

        cv2.rectangle(frame, (zone_x_start, zone_height_start), (zone_x_start + zone_width, zone_height_end),
                      (255, 0, 0), 2)

        # record detected cars
        time_now = datetime.now()
        if car_count > 0 :
            self._write_to_db(car_count, time_now, time_now.weekday())
            print('Car!!!')

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
            cv2.putText(frame_with_cars, f'Cars Count: {car_count}', (30, 450),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            # Display the frame
            cv2.imshow('Traffic Detection', frame)

            # Break the loop if 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()
