import numpy as np
import cv2 as cv
from hands import HandDetector
from canvas import Canvas
import streamlit as st
from streamlit_webrtc import webrtc_streamer
import av


def main():
    # Loading the default webcam of PC.
    #cap = cv.VideoCapture(0)
    
    # width and height for 2-D grid
    #width = int(cap.get(cv.CAP_PROP_FRAME_WIDTH) + 0.5)
    #height = int(cap.get(cv.CAP_PROP_FRAME_HEIGHT) + 0.5)

    # initialize the canvas element and hand-detector program
    canvas = Canvas(640,480)
    detector = HandDetector()
    st.title("My first Streamlit app")
    st.write("Hello, world")    
    
    # Keep looping
    def callback(frame):
        frame = frame.to_ndarray(format="bgr24")
        # Reading the frame from the camera
        frame = frame
        frame = cv.flip(frame, 1)
    
        request = detector.determine_gesture(frame)
   
        gesture = request.get('gesture')
        # if we have a gesture, deal with it
        if gesture != None:
            idx_finger = request['idx_fing_tip'] # coordinates of tip of index fing
            _, c, r = idx_finger
    
            data = {'idx_finger': idx_finger}
            rows, cols, _ = frame.shape

            # check the radius of concern 
            if (0 < c < cols and 0 < r < rows):
                if gesture == "DRAW":
                    canvas.push_point((r, c))
                elif gesture == "ERASE":
                    # stop current line
                    canvas.end_line()

                    radius = request['idx_mid_radius']

                    _, mid_r, mid_c = request['mid_fing_tip']
                    canvas.erase_mode((mid_r, mid_c), int(radius*0.5))

                    # add features for the drawing phase
                    data['mid_fing_tip'] = request['mid_fing_tip']
                    data['radius'] = radius
                elif gesture == "HOVER":
                    canvas.end_line()
                elif gesture == "TRANSLATE":
                    canvas.end_line()
                    
                    idx_position = (r, c)
                    shift = request['shift']
                    radius = request['idx_pinky_radius']
                    radius = int(radius*.8)

                    canvas.translate_mode(idx_position, int(radius*.5), shift)

                    # add features for the drawing phase
                    data['radius'] = radius
                
            frame = canvas.draw_dashboard(frame, gesture, data = data)
        else:
            frame = canvas.draw_dashboard(frame)
            canvas.end_line()
    
        # draw the stack 
        frame = canvas.draw_lines(frame)
        return av.VideoFrame.from_ndarray(frame, format="bgr24")
    webrtc_streamer(key="example", video_frame_callback=callback)
        # cv.imshow("Airdraw", frame)
    
        # stroke = cv.waitKey(1) & 0xff  
        # if stroke == ord('q') or stroke == 27: # press 'q' or 'esc' to quit
        #     break
    
    # cap.release()
    # cv.destroyAllWindows()

if __name__ == '__main__':
    main()