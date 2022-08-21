import time
import tkinter as tk
import mediapipe as mp
from PIL import ImageTk
from classifier import *
import tkinter.font as font
import random
import asyncio
from bleak import BleakClient, BleakScanner
import os

if not os.path.exists("fitness_poses_images_in"):
	os.makedirs("fitness_poses_images_in")
	os.makedirs("fitness_poses_images_in/stand")
	os.makedirs("fitness_poses_images_in/sit")

if not os.path.exists("fitness_poses_images_out"):
	os.makedirs("fitness_poses_images_out")
	os.makedirs("fitness_poses_images_out/stand")
	os.makedirs("fitness_poses_images_out/sit")

if not os.path.exists("fitness_poses_csvs_out"):
	os.makedirs("fitness_poses_csvs_out")

class gui():
	def __init__(self):
		self.root = tk.Tk()
		self.root.configure(bg='white')
		self.root.title("fall assessment")
		self.root.geometry("1024x700")
		self.root.protocol("WM_DELETE_WINDOW", self.quit_me)
		self.tab1()
		self.root.mainloop()

	def quit_me(self):
		self.root.quit()
		self.root.destroy()

	def tab1(self):
		self.label1 = tk.Label(self.root, text="Welcome to Fall Assessment V1.13", font=("Arial", 45))
		self.label1.place(relx=0.5, rely=0.05, anchor='n')
		self.label2 = tk.Label(self.root, text="Developed by Duke EGR101 Fall Assessment Team 1")
		self.label2.place(relx=0.5, rely=0.9, anchor='s')
		myFont = font.Font(size=40)
		self.button1 = tk.Button(self.root, text="Start", command=self.tab2)
		self.button1.configure(height=3, width=12)
		self.button1['font'] = myFont
		self.button1.place(relx=0.5, rely=0.5, anchor="center")

	def tab2(self):
		self.label1.destroy()
		self.label2.destroy()
		self.button1.destroy()

		self.label3 = tk.Label(self.root, text="Instructions", font=("Arial", 30))
		self.label3.pack()
		myFont = font.Font(size=25)
		self.label4 = tk.Label(self.root,
							   text="1. Place the camera 10 feet away from you\nsuch that your entire body is seen in the frame.\n2. Pivot your chair 45 degrees from the camera",
							   font=("Arial", 25)
							   )
		self.label4.pack()

		self.frame = tk.Frame(self.root, bg='white')
		self.frame.place(relx=0.5, rely=0.95, anchor="s")
		self.video_label = tk.Label(self.frame)
		self.video_label.pack()
		self.cap = cv2.VideoCapture(0)
		self.pose_tracker = mp_pose.Pose(min_detection_confidence=0.5,min_tracking_confidence=0.5)

		self.video_pre_test()

		self.button2 = tk.Button(self.root, text="Next", command=self.tab3)
		self.button2.configure(height=3, width=8)
		self.button2['font'] = myFont
		self.button2.place(relx=1, rely=0.6, anchor="e")

	def video_pre_test(self):
		mp_drawing = mp.solutions.drawing_utils
		mp_drawing_styles = mp.solutions.drawing_styles
		success, self.image = self.cap.read()
		image = self.image.copy()
		if not success:
			print("Ignoring empty camera frame.")
		image.flags.writeable = False
		image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
		results = self.pose_tracker.process(image)

		# Draw the pose annotation on the image.
		image.flags.writeable = True
		image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

		mp_drawing.draw_landmarks(
			image,
			results.pose_landmarks,
			mp_pose.POSE_CONNECTIONS,
			landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style()
		)
		image = cv2.flip(image, 3)
		cv2image = cv2.cvtColor(image, cv2.COLOR_BGR2RGBA)

		img = Image.fromarray(cv2image)
		imgtk = ImageTk.PhotoImage(image=img)
		self.video_label.imgtk = imgtk
		self.video_label.configure(image=imgtk)
		self.after_id = self.video_label.after(1, self.video_pre_test)

	def tab3(self):
		self.label3.destroy()
		self.label4.destroy()
		self.button2.destroy()
		self.label5 = tk.Label(self.root, text="Calibration", font=("Arial", 30))
		self.label5.place(relx=0.5, rely=0, anchor="n")
		self.label6 = tk.Label(self.root,
							   text="We will now calibrate this software\nPress 'Stand' to take standing pictures\nPress 'Sit' to take sitting pictures",
							   font=("Arial", 25)
							   )
		self.label6.place(relx=0.5, rely=0.08, anchor="n")
		myFont = font.Font(size=25)
		self.button3 = tk.Button(self.root, text="Sit",command=self.sit_photo)
		self.button3.configure(height=2, width=8)
		self.button3['font'] = myFont
		self.button3.place(relx=1, rely=0.4, anchor="e")

		self.button4 = tk.Button(self.root, text="Stand",command = self.stand_photo)
		self.button4.configure(height=2, width=8)
		self.button4.place(relx=1, rely=0.6, anchor="e")
		self.button4['font'] = myFont

		self.button5 = tk.Button(self.root, text="Next", command=self.tab4)
		self.button5.configure(height=2, width=8)
		self.button5['font'] = myFont
		self.button5.place(relx=1, rely=0.8, anchor="e")

	def tab4(self):
		self.label5.destroy()
		self.label6.destroy()
		self.button3.destroy()
		self.button4.destroy()
		self.button5.destroy()
		bootstrap_images_in_folder = 'fitness_poses_images_in'
		bootstrap_images_out_folder = 'fitness_poses_images_out'
		bootstrap_csvs_out_folder = 'fitness_poses_csvs_out'

		bootstrap_helper = BootstrapHelper(
			images_in_folder=bootstrap_images_in_folder,
			images_out_folder=bootstrap_images_out_folder,
			csvs_out_folder=bootstrap_csvs_out_folder,
		)
		bootstrap_helper.bootstrap()
		bootstrap_helper.align_images_and_csvs(print_removed_items=False)
		dump_for_the_app()
		class_name = 'stand'
		pose_samples_folder = 'fitness_poses_csvs_out'

		self.pose_embedder = FullBodyPoseEmbedder()


		self.pose_classifier = PoseClassifier(
			pose_samples_folder=pose_samples_folder,
			pose_embedder=self.pose_embedder,
			top_n_by_max_distance=30,
			top_n_by_mean_distance=10)

		self.pose_classification_filter = EMADictSmoothing(
			window_size=10,
			alpha=0.2)

		# Initialize counter.
		self.repetition_counter = RepetitionCounter(
			class_name=class_name,
			enter_threshold=5.8,
			exit_threshold=4.5)

		self.pose_classification_visualizer = PoseClassificationVisualizer(
			class_name=class_name,
			plot_y_max = 10
		)
		out_video_path = 'sit-stand-sample-out.mp4'
		video_width = 1024
		video_height = 768
		video_fps = self.cap.get(cv2.CAP_PROP_FPS)
		# Open output video.
		self.out_video = cv2.VideoWriter(
			out_video_path, cv2.VideoWriter_fourcc(*'mp4v'), video_fps,(video_width, video_height)
		)
		self.label8 = tk.Label(self.root,
							   text="We are about to commence the test.\nPlease return to sitting position.\nPress 'Start' when you're ready",
							   font=("Arial", 28))
		self.label8.place(relx = 0.5,rely = 0,anchor = 'n')

		self.button6 = tk.Button(self.root, text="Start!!!", command=self.tab5)
		self.button6.configure(height=2, width=8)
		myFont = font.Font(size=25)
		self.button6['font'] = myFont
		self.button6.place(relx=1, rely=0.5, anchor="e")
		self.init_count = asyncio.run(self.read())
		print(self.init_count)

	def tab5(self):
		self.label8.destroy()
		self.button6.destroy()
		self.frame_idx = 0
		self.start = time.time()
		self.now = time.time()

		self.passed = int(self.now - self.start)
		self.video_label.after_cancel(self.after_id)
		self.label7 = tk.Label(self.root, text="Time Remaining: " + str(30 - self.passed), font=('Arial', 50))
		self.label7.place(relx=0.5, rely=0.05, anchor='n')
		self.video_test()

	async def read(self):
		address = "6B:62:70:1F:F9:72"
		async with BleakClient(address) as client:
			print("connected to " + address)
			count_id = "19C20000-E8F2-537E-4F6C-D104768A1214"
			count = await client.read_gatt_char(count_id)
			count_int = bytes(count).hex()
			ret = int(count_int, 16)
			return ret

	def tab6(self):

		self.video_label.after_cancel(self.after_id2)
		self.frame.destroy()
		self.video_label.destroy()
		self.label7.destroy()
		self.button7.destroy()
		self.cap.release()

		# self.final_count = asyncio.run(self.read())
		# diff = random.randint(-1,2)

		print(self.final_count)
		hardware_count = self.final_count - self.init_count
		# hardware_count = self.repetitions_count
		# hardware_count = self.repetitions_count + diff
		# if hardware_count<0 or self.repetitions_count==0:
		# 	hardware_count = self.repetitions_count
		self.label9 = tk.Label(self.root,
							   text="Software counted " + str(self.repetitions_count),
							   font=('Arial',40))
		self.label9.pack()

		self.label12 = tk.Label(self.root,
							   text="Hardware counted " + str(hardware_count),
							   font=('Arial', 40))
		self.label12.pack()

		self.label11 = tk.Label(self.root,
							   text="Please check the CDC standards below",
							   font=('Arial',30))
		self.label11.pack()
		benchmark = Image.open('screenshots/benchmark.PNG')
		tk_benchmark = ImageTk.PhotoImage(benchmark)
		self.label10 = tk.Label(self.root,image = tk_benchmark)
		self.label10.image = tk_benchmark
		self.label10.pack()


	def video_test(self):
		if self.passed == 30:
			self.button7 = tk.Button(
				self.root, text="Check Results", command=self.tab6
			)
			self.button7.configure(height=3, width=12)
			myFont = font.Font(size=18)
			self.button7['font'] = myFont
			self.button7.place(relx=1, rely=0.5, anchor="e")
			self.final_count = asyncio.run(self.read())
			return

		# self.frame_idx+=1
		# if self.frame_idx%5 == 0:
		self.now = time.time()
		last = self.passed
		self.passed = int(self.now - self.start)
		if (last != self.passed):
			self.label7.destroy()
			self.label7 = tk.Label(self.root, text="Time Remaining: " + str(30 - self.passed),font=('Arial',50))
			self.label7.place(relx = 0.5,rely = 0.05,anchor = 'n')
		mp_drawing = mp.solutions.drawing_utils
		mp_drawing_styles = mp.solutions.drawing_styles
		success, image = self.cap.read()
		if not success:
			print("Ignoring empty camera frame.")
		image.flags.writeable = False

		image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
		results = self.pose_tracker.process(image)

		image.flags.writeable = True
		# Draw the pose annotation on the image.
		image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

		mp_drawing.draw_landmarks(
			image,
			results.pose_landmarks,
			mp_pose.POSE_CONNECTIONS,
			landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style()
		)
		image = cv2.flip(image,3)
		if results.pose_landmarks is not None:
			# Get landmarks.
			frame_height, frame_width = image.shape[0], image.shape[1]
			pose_landmarks = np.array(
				[[lmk.x * frame_width, lmk.y * frame_height, lmk.z * frame_width] for lmk in results.pose_landmarks.landmark], dtype=np.float32
			)

			# Classify the pose on the current frame.
			pose_classification = self.pose_classifier(pose_landmarks)
			# Smooth classification using EMA.
			pose_classification_filtered = self.pose_classification_filter(pose_classification)
			# Count repetitions.
			self.repetitions_count = self.repetition_counter(pose_classification)
		else:
			# No pose => no classification on current frame.
			pose_classification = None
			pose_classification_filtered = self.pose_classification_filter(dict())
			pose_classification_filtered = None
			self.repetitions_count = self.repetition_counter.n_repeats

		# Draw classification plot and repetition counter.
		image = self.pose_classification_visualizer(
			frame=image,
			pose_classification=pose_classification,
			pose_classification_filtered=pose_classification_filtered,
			repetitions_count=self.repetitions_count,
			plot_x_max=self.frame_idx + 1
		)

		self.out_video.write(cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR))

		# self.frame_idx += 1

		cv2image = cv2.cvtColor(np.array(image), cv2.COLOR_BGR2RGBA)
		# cv2image = cv2.cvtColor(image, cv2.COLOR_BGR2RGBA)
		img = Image.fromarray(cv2image)

		imgtk = ImageTk.PhotoImage(image=img)
		self.video_label.imgtk = imgtk
		self.video_label.configure(image=imgtk)

		self.after_id2 = self.video_label.after(1, self.video_test)

	def sit_photo(self):
		sit_count = 0
		while sit_count < 10:
			sit_count += 1
			self.button3.after(200,None)

			cv2.imwrite("fitness_poses_images_in/sit/%d.jpg" % sit_count, self.image)

	def stand_photo(self):
		stand_count = 0
		while stand_count < 10:
			stand_count += 1
			self.button4.after(200, None)
			cv2.imwrite("fitness_poses_images_in/stand/%d.jpg" % stand_count, self.image)

gui = gui()

