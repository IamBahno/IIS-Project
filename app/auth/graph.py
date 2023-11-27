import matplotlib.pyplot as plt
from io import BytesIO
import base64
from app.models import Value,Device, Parameter, DeviceType, values_of_device
from app import db

#takes device, return list of gprahs/images for each parameter, ordered by parameter id
def get_graphs(device):
    datas = []
    parameters = DeviceType.query.filter_by(id=device.device_type_id).first().parameters
    for parameter in parameters:
        values = values_of_device(parameter.id,device.id)
        timestamp_and_value = []
        for value in values:
            if value == None:
                timestamp_and_value = []
                break
            timestamp_and_value.append((value.timestamp,value.value))
        datas.append(timestamp_and_value)
    
    images = []


    for data,parameter in zip(datas,parameters):
        if data == []:
            images.append(None)
        fig, ax = plt.subplots(1, 1, figsize=(8, 6))
        ax.plot([entry[0] for entry in data], [entry[1] for entry in data], color='orange', marker='o', linestyle='-', linewidth=2)
        ax.set_title(parameter.name,color='white')

        ax.spines['bottom'].set_color('gray')
        ax.spines['top'].set_color('gray')
        ax.spines['right'].set_color('gray')
        ax.spines['left'].set_color('gray')
        
        ax.xaxis.label.set_color('gray')
        ax.yaxis.label.set_color('gray')
        
        ax.tick_params(axis='x', colors='gray')
        ax.tick_params(axis='y', colors='gray')
        
        ax.grid(color='lightgray', linestyle='--', linewidth=0.5)
        
        ax.set_xlabel('Timestamp')
        ax.set_ylabel('Value')
        ax.set_facecolor((0, 0, 0, 0))  # Transparent background
    
        fig.tight_layout()
        # Save the plot to a BytesIO object
        img_data = BytesIO()
        plt.savefig(img_data, format='png', transparent=True)
        img_data.seek(0)

        # Encode the image data to base64 for HTML
        img_base64 = base64.b64encode(img_data.read()).decode('utf-8')
        images.append(img_base64)
    return images