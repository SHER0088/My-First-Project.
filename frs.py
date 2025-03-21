import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.datasets import fetch_lfw_people
from sklearn.decomposition import PCA
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.neural_network import MLPClassifier
import numpy as np
import os,cv2
from sklearn.neural_network import MLPClassifier
import numpy as np
import os,cv2

def plot_gallery(images, titles, h, w, n_row=3, n_col=4):
  plt.figure(figsize=(1.8*n_col, 2.4*n_row))
  plt.subplots_adjust(bottom=0, left=.01, right=.99, top=.90, hspace=.35)
  for i in range(n_row*n_col):
    plt.subplot(n_row, n_col, i+1)
    plt.imshow(images[i].reshape((h, w)), cmap=plt.cm.gray)
    plt.title(titles[i], size=12)
    plt.xticks(())
    plt.yticks(())
    plt.subplot(n_row, n_col, i+1)
    plt.imshow(images[i].reshape((h, w)), cmap=plt.cm.gray)
    plt.title(titles[i], size=12)
    plt.xticks(())
    plt.yticks(())

from google.colab import drive
drive.mount('/content/drive')
dir_name='/content/drive/My Drive/Visual_project/dataset/faces/'
y=[];X=[];target_names=[]
person_id=0;h=w=300
n_samples=0
class_names=[]
for person_name in os.listdir(dir_name):
  dir_path = os.path.join(dir_name, person_name)
  class_names.append(person_name)
  for image_name in os.listdir(dir_path):
     image_path = os.path.join(dir_path, image_name)
     img = cv2.imread(image_path)
     # Check if image was loaded successfully
     if img is not None:
       # Convert into grayscale
       grayc = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
       # Resize image to 300*300 dimension
       resized_image = cv2.resize(grayc,(h,w))
       # Convert matrix to vector
       v = resized_image.flatten()
       X.append(v)
       # Increase the number of samples
       n_samples = n_samples+1
       # Addinng th categorical Label
       y.append(person_id)
       target_names.append(person_name)
     else:
       print(f"Could not load image: {image_path}")
  person_id = person_id+1

# Split into a traing and testing set
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)

n_components = 150

print("Extracting the top %d eigenfaces from %d faces" % (n_components, len(X_train)))

# Applying PCA
pca = PCA(n_components=n_components, svd_solver='randomized', whiten=True).fit(X_train)

# Generating eigenfaces
eigenfaces = pca.components_.reshape((n_components, h, w))

# Plot the gallery of the most significance eigenfaces
eigenface_titles = ["eigenface %d" % i for i in range(eigenfaces.shape[0])]
plot_gallery(eigenfaces, eigenface_titles, h, w)

plt.show()

print("Projecting the input data on the eigenfaces orthonormal basis")
X_train_pca = pca.transform(X_train)
X_test_pca = pca.transform(X_test)
print(X_train_pca.shape,X_test_pca.shape)

lda = LinearDiscriminantAnalysis()
# Compute LDA of reduced data
lda.fit(X_train_pca, y_train)

X_train_lda = lda.transform(X_train_pca)
X_test_lda = lda.transform(X_test_pca)
print("PROJECT SUCCESSFUL.....")

# Save pic to jpg
plt.savefig('eigenfaces.jpg')

# Training with multi layer perceptron
from sklearn.neural_network import MLPClassifier
clf = MLPClassifier(random_state=1, hidden_layer_sizes=(10,10),max_iter=1000, verbose=True).fit(X_train_lda, y_train)
print("Model Weights:")
model_info = [coef.shape for coef in clf.coefs_]
print(model_info)

y_pred=[]; y_prob=[]
for test_face in X_test_lda:
  prob = clf.predict_proba([test_face])[0]
  class_id = np.where(prob ==np.max(prob))[0][0]
  # Find the label of the mathed face
  y_pred.append(class_id)
  y_prob.append(np.max(prob))

# Transform the data
y_pred = np.array(y_pred)

prediction_titles=[]
true_positives = 0
for i in range(y_pred.shape[0]):
  true_names = class_names[y_test[i]]
  pred_name = class_names[y_pred[i]]
  result = 'pred : %s, pr: %s \ntrue: %s' % (pred_name, str(y_prob[i])[0:3],true_names)
  prediction_titles.append(result)
  if true_names==pred_name:
    true_positives = true_positives+1

print("Accuracy:",true_positives*100/y_pred.shape[0])

# # Plot results
plot_gallery(X_test,prediction_titles, h, w)
plt.show()

# Save the pic to jpg
plt.savefig('results.jpg')

