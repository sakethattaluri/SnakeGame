# SnakeGame
This is my attempt to automate the snake in classic Snake Game using Machine Learning.  
Two classifiers are used to predict the new direction as mentioned in Pandas section
* **Threshold classifier** predicts the direction by considering all the features. This classifier is triggered only if the distance of the head and any of the obstacle is less than 5% of the total length of the window in that direction
* **Normal classifier** predicts the direction by considering only current direction and slope(from egg to head of the snake). 

## How to run the game
1. Run *snake_game_manual.py* and play the game manually
2. This generates training data *Data.xlsx*. Size of the training set depends on the amount of time you play the game
3. Run *snake_game_auto.py*

## Python Libraries used
Pygame, Pandas, sklearn and graphviz are the four main modules used

### Pygame
To create the GUI of the game

### Pandas
To work with feature set. 6 features are used to train the model (Distance of the head from four directions(body of the snake or boundaries of the window), current direction of the head, slope of the line from egg to head of the snake)

### sklearn
To train the model and predict the output. DecisionTree classifier was used here which gave better accuracy than SVM. After the classification, the model predicts the new direction(up/down/right/left) based on the input. 

### graphviz
This library is optional. It is used to print the decision tree to a PDF file

## Future Scope
I have generated the model based on the limitied training set(~750 instances) obtained by running *snake_game_manual.py*. It need to be larger in order to cover maximum scenarios. Then, model need to be refined to get the best test and train accuracy
