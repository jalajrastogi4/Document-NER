from flask import Flask, request
from flask import render_template
import settings
import utils
import numpy as np
import predictions as pred
import cv2

app = Flask(__name__)
app.secret_key = 'document_scanner_app'

docscan = utils.DocumentScan()

@app.route('/', methods=['GET', 'POST'])
def scandoc():
    if request.method == 'POST':
        file = request.files['image_name']
        upload_image_path = utils.save_upload_image(file)
        print('Image saved in : ', upload_image_path)
        # predict the coordinates of document
        four_points, size = docscan.document_scanner(upload_image_path)
        print(four_points, size)
        if four_points is None:
            message = 'UNABLE TO LOCATE THE COORDINATES: points displayed are random'
            points = [
                {'x':10, 'y':10},
                {'x':120, 'y':10},
                {'x':120, 'y':120},
                {'x':10, 'y':120},
            ]
            return render_template('scanner.html', 
                                   points=points, 
                                   fileupload=True, 
                                   message=message)
        else:
            points = utils.array_to_json(four_points)
            message = 'DETECTED THE COORDINATES SUCCESSFULLY'
            return render_template('scanner.html',
                                   points=points, 
                                   fileupload=True, 
                                   message=message)
        
        return render_template('scanner.html')
        
    return render_template('scanner.html')


@app.route('/transform', methods=['POST'])
def transform():
    try:
        points = request.json['data']
        array = np.array(points)
        print('caliberating.........')
        magic_color = docscan.caliberate_to_orginal_size(array)
        print('saving image.........')
        utils.save_magic_image(magic_color, 'magic_color.jpg')
        return 'success'
    except Exception as e:
        print(repr(e))
        return 'Error'
    
    
@app.route('/prediction')
def prediction():
    wrap_image_filepath = settings.join_path(settings.MEDIA_DIR, 'magic_color.jpg')
    image = cv2.imread(wrap_image_filepath)
    image_bb, results = pred.getPredictions(image)
    
    bb_filename = settings.join_path(settings.MEDIA_DIR, 'bounding_box.jpg')
    cv2.imwrite(bb_filename, image_bb)
    
    return render_template('predictions.html', results=results)



if __name__ == '__main__':
    app.run(debug=True)