django.jQuery(document).ready(function($) {
    function autofillDiagnosis(patientId) {
        if (!patientId) {
            return;
        }
        var diagnosisField = $('#id_diagnosis');
        if (diagnosisField.val().trim() !== '') {
            return;
        }
        $.ajax({
            url: '/admin/patients/patientcard/get-patient-diagnosis/' + patientId + '/',
            method: 'GET',
            success: function(data) {
                diagnosisField.val(data.diagnosis);
            }
        });
    }

    $('#id_patient').on('change', function() {
        autofillDiagnosis($(this).val());
    });

    $(document).on('select2:select', '#id_patient', function(e) {
        autofillDiagnosis(e.params.data.id);
    });
});