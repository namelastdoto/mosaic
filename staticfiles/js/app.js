const imageElement = document.getElementById('image');
const inputElement = document.getElementById('imageInput');
const sendBtn = document.getElementById('sendBtn');
const zoomInBtn = document.getElementById('zoomIn');
const zoomOutBtn = document.getElementById('zoomOut');
const moveLeftBtn = document.getElementById('moveLeft');
const moveRightBtn = document.getElementById('moveRight');
const moveUpBtn = document.getElementById('moveUp');
const moveDownBtn = document.getElementById('moveDown');
let cropper;

inputElement.addEventListener('change', function() {
    const file = this.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(event) {
            imageElement.src = event.target.result;
            if (cropper) {
                cropper.destroy();
            }
            cropper = new Cropper(imageElement, {
                aspectRatio: 1/1.33,
                viewMode: 1,
                autoCropArea: 1,
                cropBoxResizable: false,
                });
        }
        reader.readAsDataURL(file);
    }
});

zoomInBtn.addEventListener('click', function() {
    cropper.zoom(0.1);
});

zoomOutBtn.addEventListener('click', function() {
    cropper.zoom(-0.1);
});

moveLeftBtn.addEventListener('click', function() {
    cropper.move(-10, 0);
});

moveRightBtn.addEventListener('click', function() {
    cropper.move(10, 0);
});

moveUpBtn.addEventListener('click', function() {
    cropper.move(0, -10);
});

moveDownBtn.addEventListener('click', function() {
    cropper.move(0, 10);
});

sendBtn.addEventListener('click', function() {
    if (cropper) {
        const croppedCanvas = cropper.getCroppedCanvas();
        const base64Data = croppedCanvas.toDataURL();
        sendDataToServer(base64Data);
    }
});

function sendDataToServer(base64Data) {
    document.getElementById('overlay').style.display = 'block';
    setTimeout(() => {
        fetch('/api/examples/upload/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ image: base64Data }),
        })
         .then(response => response.json())
         .then(data => {
            document.getElementById('mosaic1').src = data.mosaic1;
            document.getElementById('mosaic2').src = data.mosaic2;
            document.getElementById('mosaic3').src = data.mosaic3;
            document.getElementById('overlay').style.display = 'none';

            $('#responseModal').modal('show');
        })
        .catch(error => {
            console.error('Error:', error);
            document.getElementById('spinner').style.display = 'none';
            alert('error : ( try again');
        });
    }, 0010);
}