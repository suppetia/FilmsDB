from pyzbar import pyzbar
import cv2
import imutils
from imutils.video import VideoStream


def scan_image(image):

    barcodes = pyzbar.decode(image)
    print(barcodes)

    # loop over the detected barcodes
    for barcode in barcodes:
        # extract the bounding box location of the barcode and draw the
        # bounding box surrounding the barcode on the image
        (x, y, w, h) = barcode.rect
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)
        # the barcode data is a bytes object so if we want to draw it on
        # our output image we need to convert it to a string first
        barcodeData = barcode.data.decode("utf-8")
        barcodeType = barcode.type
        # draw the barcode data and barcode type on the image
        text = "{} ({})".format(barcodeData, barcodeType)
        cv2.putText(image, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, (0, 0, 255), 2)
        # print the barcode type and data to the terminal
        print("[INFO] Found {} barcode: {}".format(barcodeType, barcodeData))

        return barcodeData


def scan_camera_input():
    barcode = None
    vs = VideoStream().start()
    # loop over the frames from the video stream
    while True:
        # grab the frame from the threaded video stream and resize it to
        # have a maximum width of 640 pixels
        frame = vs.read()
        frame = imutils.resize(frame, width=640)
        # show the output frame
        cv2.imshow("Barcode Scanner", frame)
        key = cv2.waitKey(1) & 0xFF

        barcode = scan_image(frame)
        if barcode:
            break

        # if the `q` key was pressed, break from the loop
        if key == ord("q"):
            break
    # close the output CSV file do a bit of cleanup
    print("[INFO] cleaning up...")

    cv2.destroyAllWindows()
    vs.stop()
    return barcode
