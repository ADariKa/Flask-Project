ClassicEditor
    .create(document.querySelector('#editor'), {

        toolbar: {
            items: [
                'heading',
                '|',
                'bold',
                'italic',
                'link',
                'bulletedList',
                'numberedList',
                '|',
                'indent',
                'outdent',
                '|',
                'undo',
                'redo',
                'imageUpload',
                'CKFinder',
                'mediaEmbed',
                'blockQuote',
                'insertTable',
                'alignment',
                'code',
                'codeBlock',
                'fontBackgroundColor',
                'fontColor',
                'fontSize',
                'fontFamily',
                'horizontalLine'
            ]
        },
        language: 'ru',
        image: {
            toolbar: [
                'imageTextAlternative',
                'imageStyle:full',
                'imageStyle:side'
            ]
        },
        table: {
            contentToolbar: [
                'tableColumn',
                'tableRow',
                'mergeTableCells'
            ]
        },
        licenseKey: '',
        ckfinder: {
            // Upload the images to the server using the CKFinder QuickUpload command.
            uploadUrl: '/upload-image?command=QuickUpload&type=Files&responseType=json'
        },
        mediaEmbed: {
            previewsInData: true
        }

    })
    .then(editor => {
        window.editor = editor;
        console.log('Connect CKEditor success');
    })
    .catch(error => {
        console.error('Oops, something gone wrong!');
        console.error('Please, report the following error in the https://github.com/ckeditor/ckeditor5 with the build id and the error stack trace:');
        console.warn('Build id: m2wdkjmyzmt6-q1tvn0qbl8fi');
        console.error(error);
    });