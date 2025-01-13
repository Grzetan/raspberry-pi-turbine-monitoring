import cv2
import numpy as np
import time


def paint_outside_circle(image, center, radius):
    # Create a mask with the same dimensions as the image
    mask = np.zeros(image.shape[:2], dtype=np.uint8)

    # Draw a filled white circle on the mask
    cv2.circle(mask, center, radius, 255, -1)

    # Create a white image with the same dimensions and type as the input image
    white_background = np.ones_like(image) * 127

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

    frame_count = 0
    start_time = time.time()

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Reached end of video or failed to read frame.")
            break
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        frame = paint_outside_circle(frame, (590, 900), 880)

        _, mask1 = cv2.threshold(frame, 200, 255, cv2.THRESH_BINARY)
        _, mask2 = cv2.threshold(frame, 40, 255, cv2.THRESH_BINARY_INV)
        mask = cv2.bitwise_or(mask1, mask2)

        # Find the most left, right, top, and bottom pixel
        coords = np.column_stack(np.where(mask == 255))
        if len(coords) == 0:
            continue

        leftmost = coords[coords[:, 1].argmin()]
        rightmost = coords[coords[:, 1].argmax()]
        topmost = coords[coords[:, 0].argmin()]
        bottommost = coords[coords[:, 0].argmax()]

        # Calculate the center
        cX = (leftmost[1] + rightmost[1]) // 2
        cY = (topmost[0] + bottommost[0]) // 2

        # Draw the center on the mask
        cv2.circle(mask, (cX, cY), 10, (127), -1)

        cv2.imshow("Frame", mask)

        cv2.waitKey(0)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
        frame_count += 1

    end_time = time.time()
    elapsed_time = end_time - start_time
    fps = frame_count / elapsed_time
    print(f"FPS: {fps:.2f}")

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
