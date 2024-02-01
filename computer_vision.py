import os
import cv2
import psycopg2
import numpy as np
from datetime import datetime


class CarCount:
    def __init__(self, url, cascade, db_name, db_user, db_pass, db_host, db_port=5432):
        self.frame_counter = 0
        self.frame_date = datetime.min
        self.cascade = cascade
        self.db_name = db_name
        self.db_user = db_user
        self.db_pass = db_pass
        self.db_host = db_host
        self.db_port = db_port

        self.generate_frames(url)

    def _load_car_cascade(self):
        """Load the Haar Cascade for car detection."""
        try:
            file_path = os.path.join(os.path.dirname(__file__), self.cascade)
            if not os.path.exists(file_path):
                raise FileNotFoundError("Haar cascade file not found.")

            return cv2.CascadeClassifier(file_path)
        except Exception as e:
            print(f"Error loading Haar cascade: {e}")
            return None

    def _write_to_db(self, count, date, day):
        """Write detected car count to PostgreSQL database."""
        try:
            with psycopg2.connect(database=self.db_name, user=self.db_user, password=self.db_pass,
                                  host=self.db_host, port=self.db_port) as conn:
                with conn.cursor() as cur:
                    query = "INSERT INTO car_statistics (day, date, count) VALUES (%s, %s, %s)"
                    cur.execute(query, (day, date, count))
                    conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print("Error while writing to PostgreSQL", error)

    def _detect_cars(self, frame, car_cascade):
        """Detect cars in the frame and draw rectangles around them."""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        cars = car_cascade.detectMultiScale(gray, 1.1, 3)

        zone_width, zone_height_start, zone_height_end, zone_x_start = self._calculate_zone(frame)

        car_count = 0
        for (x, y, w, h) in cars:
            if self._is_car_in_zone(x, y, w, h, zone_x_start, zone_width, zone_height_start, zone_height_end):
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                car_count += 1

        cv2.rectangle(frame, (zone_x_start, zone_height_start), (zone_x_start + zone_width, zone_height_end),
                      (255, 0, 0), 2)

        self._record_car_count(car_count)

        return frame, car_count

    def _calculate_zone(self, frame):
        height, width = frame.shape[:2]
        zone_width = int(width * 0.8)
        zone_height_start = int(height * 0.08)
        zone_height_end = height
        zone_x_start = width // 2 - zone_width // 2
        return zone_width, zone_height_start, zone_height_end, zone_x_start

    def _is_car_in_zone(self, x, y, w, h, zone_x_start, zone_width, zone_height_start, zone_height_end):
        return zone_x_start <= x <= zone_x_start + zone_width - w and zone_height_start <= y <= zone_height_end - h

    def _record_car_count(self, car_count):
        if car_count > 0:
            time_now = datetime.now()
            self._write_to_db(car_count, time_now, time_now.weekday())
            print('Car detected.')

    def generate_frames(self, url):
        """Generate frames from the video and process for car detection."""
        cap = cv2.VideoCapture(url)
        car_cascade = self._load_car_cascade()

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame_with_cars, car_count = self._detect_cars(frame, car_cascade)
            cv2.putText(frame_with_cars, f'Cars Count: {car_count}', (30, 750),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.imshow('Traffic Detection', frame_with_cars)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()
