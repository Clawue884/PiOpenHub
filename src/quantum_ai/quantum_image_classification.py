# src/quantum_ai/quantum_image_classification.py

import numpy as np
from qiskit import QuantumCircuit, Aer, execute
from qiskit.circuit.library import RealAmplitudes
from qiskit_machine_learning.algorithms import VQC
from sklearn.datasets import fetch_openml
from sklearn.model_selection import train_test_split
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score
from sklearn.pipeline import make_pipeline
from sklearn.ensemble import RandomForestClassifier

class QuantumImageClassification:
    def __init__(self, n_qubits):
        self.n_qubits = n_qubits
        self.backend = Aer.get_backend('aer_simulator')

    def create_circuit(self, params):
        """Create a quantum circuit for classification."""
        qc = QuantumCircuit(self.n_qubits)

        # Apply rotation gates based on input parameters
        for i in range(self.n_qubits):
            qc.ry(params[i], i)

        qc.measure_all()  # Measure all qubits
        return qc

    def train_quantum_model(self, X_train, y_train):
        """Train a variational quantum classifier."""
        feature_map = RealAmplitudes(num_qubits=self.n_qubits, reps=2)
        ansatz = RealAmplitudes(num_qubits=self.n_qubits, reps=2)

        vqc = VQC(feature_map=feature_map, ansatz=ansatz, optimizer='SLSQP', backend=self.backend)
        vqc.fit(X_train, y_train)

        return vqc

    def predict(self, model, X_test):
        """Make predictions using the trained model."""
        predictions = []
        for x in X_test:
            # Create a circuit for each input
            qc = self.create_circuit(x)
            job = execute(qc, self.backend, shots=1024)
            result = job.result()
            counts = result.get_counts()
            prediction = max(counts, key=counts.get)  # Get the most frequent outcome
            predictions.append(prediction)
        return predictions

    def train_classical_model(self, X_train, y_train):
        """Train a classical model for comparison."""
        model = make_pipeline(StandardScaler(), PCA(n_components=10), RandomForestClassifier(n_estimators=100))
        model.fit(X_train, y_train)
        return model

    def evaluate_model(self, model, X_test, y_test):
        """Evaluate the model's performance."""
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        return accuracy

# Example usage
if __name__ == "__main__":
    # Load the MNIST dataset
    mnist = fetch_openml('mnist_784', version=1)
    X = mnist.data[:1000]  # Use a subset for simplicity
    y = mnist.target[:1000]

    # Convert labels to integers
    y = y.astype(int)

    # Split the dataset
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Create and train the quantum image classification model
    n_qubits = 4  # Number of qubits (adjust based on feature size)
    quantum_classifier = QuantumImageClassification(n_qubits)

    # Train the quantum model
    model = quantum_classifier.train_quantum_model(X_train, y_train)

    # Train a classical model for comparison
    classical_model = quantum_classifier.train_classical_model(X_train, y_train)

    # Evaluate both models
    quantum_accuracy = quantum_classifier.evaluate_model(model, X_test, y_test)
    classical_accuracy = quantum_classifier.evaluate_model(classical_model, X_test, y_test)

    print(f"Quantum Model Accuracy: {quantum_accuracy:.2f}")
    print(f"Classical Model Accuracy: {classical_accuracy:.2f}")
