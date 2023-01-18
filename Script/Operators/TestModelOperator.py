import numpy as np
from Script.Operators import AIOperator as aio

ai_op = aio.Operator()


class Operator:

    def __init__(self):
        print(" *** TEST MODEL OPERATOR LOADED SUCCESSFULLY")

    def test_model(self, global_op, model_op, sessions, model_path, target):
        test_samples, test_labels = global_op.convert_data(sessions, target)
        model = model_op.load_model(model_path)

        true_predictions = 0
        false_predictions = 0
        total_predictions = 0

        for idx in range(0, len(test_samples)):

            feature_set = test_samples[idx]
            true_label = test_labels[idx]

            reshape_set = []
            if target == 0:
                reshape_set = (np.array(feature_set)).reshape(-1, 5)
            elif target == 1:
                reshape_set = (np.array(feature_set)).reshape(-1, 4)
            elif target == 2:
                reshape_set = (np.array(feature_set)).reshape(-1, 3)

            prediction = ai_op.predict_feature(model, reshape_set)

            total_predictions += 1

            if prediction == true_label:
                true_predictions += 1
            else:
                false_predictions += 1

        print(" *** model: " + str(model_path))
        print(" *** total_predictions: " + str(total_predictions))
        print(" *** true_predictions: " + str(true_predictions))
        print(" *** false_predictions: " + str(false_predictions))
        print(" *** accuracy: " + str(round(true_predictions / total_predictions, 3)))
