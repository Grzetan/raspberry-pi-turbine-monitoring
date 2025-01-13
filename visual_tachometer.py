import cv2
import numpy as np


def paint_outside_circle(image, center, radius, color=127):
    # Create a mask with the same dimensions as the image
    mask = np.zeros(image.shape[:2], dtype=np.uint8)

    # Draw a filled white circle on the mask
    cv2.circle(mask, center, radius, 255, -1)

    # Create a white image with the same dimensions and type as the input image
    white_background = np.ones_like(image) * color

    # Combine the original image and the white background using the mask
    result = cv2.bitwise_and(image, image, mask=mask)
    inverted_mask = cv2.bitwise_not(mask)
    result += cv2.bitwise_and(white_background, white_background, mask=inverted_mask)

    return result


def main():
    video_path = "videos/2.mp4"
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print("Error: Could not open video.")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Reached end of video or failed to read frame.")
            break

        frame = paint_outside_circle(frame, (590, 900), 700, 255)
        frame = paint_outside_circle(frame, (590, 900), 880, 0)

        cv2.imshow("Frame", frame)

        cv2.waitKey(0)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
