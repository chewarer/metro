$(function () {
  /* 1. OPEN THE FILE EXPLORER WINDOW */
  $(".js-upload-photos").click(function () {
    $("#fileupload").click();
  });

  /* 2. INITIALIZE THE FILE UPLOAD COMPONENT */
  $("#fileupload").fileupload({
    dataType: 'json',
    sequentialUploads: true,  /* 1. SEND THE FILES ONE BY ONE */
    // send: function (e, data) {
    //   console.log(data);
    // },
    start: function (e) {  /* 2. WHEN THE UPLOADING PROCESS STARTS, SHOW THE MODAL */
      $("#modal-progress").modal("show");
    },
    stop: function (e) {  /* 3. WHEN THE UPLOADING PROCESS FINALIZE, HIDE THE MODAL */
      $("#modal-progress").modal("hide");
    },
    progressall: function (e, data) {  /* 4. UPDATE THE PROGRESS BAR */
      var progress = parseInt(data.loaded / data.total * 100, 10);
      var strProgress = progress + "%";
      $(".progress-bar").css({"width": strProgress});
      $(".progress-bar").text(strProgress);
    },
    done: function (e, data) {
      if (data.result.is_valid) {
        $("#gallery tbody").prepend(
          "<tr data-weight='1'><td><img src='" + data.result.thumb + "'></td><td><a href='" + data.result.url + "'>" + data.result.name + "</a></td><td><div class='btn btn-sm btn-danger delete del-photo' data-url='" + data.result.pk + "'><i class='glyphicon glyphicon-trash'></i> удалить</div></td></tr>"
        );
      }
    }

  });



    // Удаление файла
    $("body" ).on( "click", '.del-photo', function() {
        pk = $(this).attr('data-url');
        object_id = $('#edit-object').attr('data-obj_id');
        // alert(url);
        row = $(this).parent().parent();
        $.ajax({
            url: '/login/object/delete/photo/' + pk,
            dataType: 'json',
            type: 'GET',
            data: {'object_id': object_id},
            success: function (data) {
                // console.log(JSON.stringify(data));
                if (data['status'] == 'ok') {
                    row.remove();
                }
            }
        });
    });

    // Сохранение сортировки
    $('body').on('click', '#sort-save', function() {
        save_sort()
    });

    function save_sort() {
        var data_list = [];
        $('#gallery tbody .del-photo').each(function (index) {
           pid = $(this).attr('data-url');
           weight = $(this).parent().parent().attr('data-weight');
           data_list.push({'id': pid, 'weight': weight});
        });
        data = JSON.stringify(data_list);
        console.log(data);
        // Отправка порядка сортировки
        $.ajax({
            url: '/login/object/save-weight/',
            dataType: 'json',
            type: 'GET',
            data: {'data': data},
            success: function (data) {
                // console.log(data);
            }
        });
    }

    $('#gallery tbody').sortable({
        update: function(event, ui) {
            $('#gallery tr').each(function(i) {
               $(this).data('weight', i+1);
               $(this).attr('data-weight', i + 1);
            }).filter(':first').trigger('listData');
        }
    });
    // $('#gallery tr').on('listData', function() {
    //     $('#gallery tr').each(function() {
    //     $(this).attr('data-weight', i + 1);
    //        console.log( $(this).text() + ' - ' + $(this).data('weight') );
    //     });
    // });

});
