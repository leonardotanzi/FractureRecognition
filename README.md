# fractureDetection
Fracture detection project for a Computer Vision course at Politecnico di Torino.

# Participants
Il grande Leonardo Tanzi

Il fenomeno francese Fabien Cassassolles

# How it works
The main idea is to use the combined action of two predictors.
* A set of classic Computer Vision filters are applied to the image
* A first predictor is used based on the Hough transform. It will detect the major lines in the image, and the angle
they form with a reference. If several angles appear frequently, it might highlight a bone fracture.
* A second predictor is the presence of great angle values between the main lines of the X-ray image. They might result
in a 

# Improvements
* Refine parameters
* With a potential high CPU and GPU a Deep Learning approach could be interesting
    * CNN might be the optimal way to go as it is a standard approach to image recognition and could work for fracture
    classification
    * A Random Forest or a decision tree model could be a good way to start classifying diverse types of fractures