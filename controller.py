import data_reader
import triplets_mining
import CNN_triplet_loss_functional
import loading_weights
import numpy as np

#get training data
training_data = data_reader.get_training_set()

#increase the data by doing transformations as described in the paper
images, labels = data_reader.increase_data(training_data[0], training_data[1])

#get random triplets for the first iteration of mining
triplets = triplets_mining.get_random_triplets(30000, images, labels)

#Get triplets ready as input for the network
# l is the number of elements in each triplet
l, triplets =triplets_mining.prepare_triplets(60, 160, triplets)

#get validation set
val_images, val_labels = data_reader.get_validation_set()

#Build the model using triplet loss and sigmoid activation
model = CNN_triplet_loss_functional.build_model(60, 160)
print(model.summary())

#declare arrays to store accuracy, precision, recall and F1 score
accuracy, precision, recall, f1_score = [], [], [], []

history = CNN_triplet_loss_functional.AccuracyHistory()
num_epochs = 30
for epoch in range(num_epochs):
    print('Epoch %s' % epoch)
    model.fit(triplets,
            y=np.zeros(l),
            batch_size=120,
            epochs=1,
            verbose=1,
            callbacks=[history])

    np.save("triplet_loss_sigmoid_weights",
            model.layers[3].get_weights())

    validation_output_dict = loading_weights.build_dict(
        "triplet_loss_sigmoid_weights", val_images, val_labels)
    alpha = 0.1
    t_p, f_n = loading_weights.true_positives_and_false_negatives(
        validation_output_dict, alpha)
    f_p, t_n = loading_weights.false_positives_and_true_negatives(
        validation_output_dict, alpha)

    precision.append(t_p/(t_p + f_p))
    recall.append(t_p/(t_p + f_n))
    accuracy.append((t_p + t_n)/(t_p + f_n + f_p + t_n))
    f1_score.append(2*((precision*recall)/(precision+recall)))

#Print performance measures
validation_output_dict = loading_weights.build_dict(
    "triplet_loss_sigmoid_weights", val_images, val_labels)
alpha = 0.1
loading_weights.print_performance_measures(validation_output_dict, alpha)

#Print performance measures history
print("")
print("Precision History")
print(precision)
print("")
print("Recall History")
print(recall)
print("")
print("Accuracy History")
print(accuracy)
print("")
print("F1 score History")
print(f1_score)
