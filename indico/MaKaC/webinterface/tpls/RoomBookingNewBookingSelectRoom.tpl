<h2 class="page-title">
    ${ _('Book a room') }
</h2>

<ul id="breadcrumbs" style="margin: 0px 0px 0px -15px; padding: 0; list-style: none;">
    <li><span class="current">${ _('Specify Search Criteria') }</span></li>
    <li><span>${ _('Select Available Period') }</span></li>
    <li><span>${ _('Confirm Reservation') }</span></li>
</ul>


% if errors:
    <div class="error-message-box">
        <div class="message-text">
            ${ _("There are some errors in the search criteria:") }
            <ul>
                % for error in errors:
                    <li>${ error }</li>
                % endfor
            </ul>
        </div>
    </div>
% endif

<form id="searchForm" method="POST" action="">
    <input type="hidden" name="step" value="1">
    <table id="roomBookingTable" cellspacing="0" style="width: 100%;">
        <tr>
            <td>
                <h2 class="group-title">
                    <i class="icon-location"></i>
                    ${ _('Rooms') }
                </h2>
            </td>
        </tr>
        <!-- ROOMS -->
        <tr>
            <td>
                <div id="roomselector"></div>
            </td>
        </tr>
        <!-- DATES -->
        <tr>
            <td>
                <h2 class="group-title"><i class="icon-calendar"></i>${ _('Date range') }</h2>
            </td>
        </tr>
        <tr>
            <td>
                <div class="toolbar thin">
                    <div id="repeatability" class="group i-selection">
                        <span class="i-button label">${ _('Frequency') }</span>
                        <input type="radio" id="once" value="None" name="repeatability" checked>
                        <label for="once" class="i-button">${ _('Once') }</label>
                        <input type="radio" id="daily" value="0" name="repeatability">
                        <label for="daily" class="i-button">${ _('Daily') }</label>
                        <input type="radio" id="weekly" value="1" name="repeatability">
                        <label for="weekly" class="i-button">${ _('Weekly') }</label>
                        <input type="radio" id="monthly" value="4" name="repeatability">
                        <label for="monthly" class="i-button">${ _('Monthly') }</label>
                    </div>
                    <div id="flexibleDates" class="group i-selection">
                        <span class="i-button label">${ _('Flexibility') }</span>
                        <input type="radio" value="0" id="0d" name="flexible_dates_range" checked>
                        <label for="0d" class="i-button">${ _('Exact') }</label>
                        <input type="radio" value="1" id="1d" name="flexible_dates_range">
                        <label for="1d" class="i-button"><sup>+</sup>/<sub>-</sub> ${ _('1 day') }</label>
                        <input type="radio" value="2" id="2d" name="flexible_dates_range">
                        <label for="2d" class="i-button"><sup>+</sup>/<sub>-</sub> ${ _('2 days') }</label>
                        <input type="radio" value="3" id="3d" name="flexible_dates_range">
                        <label for="3d" class="i-button"><sup>+</sup>/<sub>-</sub> ${ _('3 days') }</label>
                    </div>
                </div>
                <div id="sDatePlaceDiv" class="titleCellFormat bookDateDiv" style="clear: both;">
                    <div id="sDatePlaceTitle" class="label">${ _('Booking date') }</div>
                    <div id="sDatePlace"></div>
                </div>
                <div id="eDatePlaceDiv" class="titleCellFormat bookDateDiv" style="display:none;">
                    <div id='eDatePlaceTitle' class='label'>${ _('End date') }</div>
                    <div id="eDatePlace"></div>
                </div>
                <div class="infoMessage" id="holidays-warning" style="float: left; display: none"></div>
                <input name="finishDate" id="finishDate" type="hidden">
                <input name="sDay" id="sDay" type="hidden">
                <input name="sMonth" id="sMonth" type="hidden">
                <input name="sYear" id="sYear" type="hidden">
                <input name="eDay" id="eDay" type="hidden">
                <input name="eMonth" id="eMonth" type="hidden">
                <input name="eYear" id="eYear" type="hidden">
                <input name="start_date" id="start_date" type="hidden">
                <input name="end_date" id="end_date" type="hidden">
                <input name="repeat_step" id="repeat_step" type="hidden">
                <input name="repeat_unit" id="repeat_unit" type="hidden">
            </td>
        </tr>
        <!-- TIME -->
        <tr>
            <td>
                <h2 class="group-title"><i class="icon-time"></i>${ _('Time range') }</h2>
            </td>
        </tr>
        <tr>
            <td>
                <div id="timerange"></div>
            </td>
        </tr>
        <!-- SUBMIT BUTTON -->
        <tr>
            <td>
                <div class="groupTitle bookingTitle"></div>
            </td>
        </tr>
        <tr>
            <td>
                <button type="submit" class="i-button highlight">${ _('Continue') }</button>
            </td>
        </tr>
    </table>
</form>

<script>
    var userId = "rb-user-${ user.getId() if _session.user else 'not-logged' }";
    var rbUserData = $.jStorage.get(userId, {});
    var maxRoomCapacity = ${ max_room_capacity };
    var rooms = ${ [r.to_serializable('__public_exhaustive__') for r in rooms] | j, n };

    $(document).ready(function() {
        initWidgets();
        eventBindings();
        restoreUserData();

        function initWidgets() {
            $('#roomselector').roomselector({
                allowEmpty: false,
                rooms: rooms,
                roomMaxCapacity: maxRoomCapacity,
                userData: rbUserData,
                selectName: 'room_ids'
            });

            // Calendars init
            $('#sDatePlace, #eDatePlace').datepicker({
                minDate: 0,
                showButtonPanel: true,
                changeMonth: true,
                changeYear: true,
                onSelect: function(selectedDate) {
                    if ($('#sDatePlace').datepicker('getDate') > $('#eDatePlace').datepicker('getDate')) {
                        $('#eDatePlace').datepicker('setDate', $('#sDatePlace').datepicker('getDate'));
                    }
                    // TODO: clean this mess up!
                    validateForm(false);
                    combineValues();
                }
            });

            // Time slider init
            $('#timerange').timerange({
                initStartTime: '8:30',
                initEndTime: '17:30',
                startTimeName: 'sTime',
                endTimeName: 'eTime'
            });
        }

        function combineValues() {
            $('#start_date').val(
                $('#sDay').val() + '-' +
                $('#sMonth').val() + '-' +
                $('#sYear').val() + ' ' +
                $('#timerange').timerange('getStartTime')
            );
            $('#end_date').val(
                $('#eDay').val() + '-' +
                $('#eMonth').val() + '-' +
                $('#eYear').val() + ' ' +
                $('#timerange').timerange('getEndTime')
            );
            var repeatability = $('#repeatability input:checked').val();
            var unit = 0;
            var step = 0;

            if (repeatability == 'None') {
                unit = 0;
                step = 0;
            } else if (repeatability == '0') {
                unit = 1;
                step = 1;
            } else if (repeatability == '1') {
                unit = 2;
                step = 1;
            } else if (repeatability == '2') {
                unit = 2;
                step = 2;
            } else if (repeatability == '3') {
                unit = 2;
                step = 3;
            } else if (repeatability == '4') {
                unit = 3;
                step = 1;
            }
            $('#repeat_unit').val(unit);
            $('#repeat_step').val(step);
        }

        function eventBindings() {
            $('#searchForm').submit(function(e) {
                if (!validateForm(true)) {
                    new AlertPopup($T("Error"), $T('There are errors in the form. Please correct fields with red background.')).open();
                    e.preventDefault();
                } else if (!$("#roomselector").roomselector("validate")) {
                    new AlertPopup($T("Error"), $T('Please select a room (or several rooms).')).open();
                    e.preventDefault();
                } else {
                    saveFormData();
                }
            });

            $("#repeatability input:radio[name=repeatability]").change(function() {
                if ($(this).val() == 'None') {
                    $('#sDatePlaceTitle').text("${ _('Booking date') }");
                    $('#finishDate').val('false');
                    $('#eDatePlaceDiv').hide();
                } else {
                    $('#sDatePlaceTitle').text("${_('Start date')}");
                    $('#finishDate').val('true');
                    $('#eDatePlaceDiv').show();
                }

                if ($(this).val() == '0') {
                    $('#flexibleDatesDiv').hide();
                    $("#flexibleDates input:radio").prop("disabled", true);
                } else {
                    $("#flexibleDates input:radio").prop("disabled", false);
                }
            });
        }

        function restoreUserData() {
            if (rbUserData.sDay) {
                $("#sDatePlace").datepicker('setDate', new Date(rbUserData.sYear + "/" + rbUserData.sMonth + "/" + rbUserData.sDay));
                $("#eDatePlace").datepicker('setDate', new Date(rbUserData.eYear + "/" + rbUserData.eMonth + "/" + rbUserData.eDay));
            }

            $("#finishDate").val(rbUserData.finishDate);
            $("#repeatability input[name=repeatability][value=" + rbUserData.repeatability + "]")
                    .prop('checked', true)
                    .change();
            $("#flexibleDates input[name=flexible_dates_range][value=" + rbUserData.flexible_dates_range + "]")
                    .prop('checked', true);

            if (rbUserData.sTime) {
                $('#timerange')
                        .timerange('setStartTime', rbUserData.sTime)
                        .timerange('setEndTime', rbUserData.eTime)
            }
        }

        // Reads out the invalid textboxes and returns
        // false if something is invalid and
        // true if form may be submited.
        function validateForm(onlyLocal) {
            combineValues();
            var searchForm = $('#searchForm');
            $('.invalid', searchForm).removeClass('invalid');

            var isValid = true;
            var repeatability = $("#repeatability input:radio[name='repeatability']:checked").val();

            if (!onlyLocal) {
                saveCalendarData($('#finishDate').val());
                var holidaysWarning = indicoSource('roomBooking.getDateWarning', searchForm.serializeObject());
                holidaysWarning.state.observe(function(state) {
                    if (state == SourceState.Loaded) {
                        $('#holidays-warning').html(holidaysWarning.get());
                        if (holidaysWarning.get() == '')
                            $('#holidays-warning').hide();
                        else
                            $('#holidays-warning').show();
                    }
                });
            }

            updateDateRange();
            isValid = validate_period(true, true, 1, repeatability) && isValid; // 1: validate dates

            // Time validator
            isValid = isValid && $('#timerange').timerange('validate');

            return isValid;
        }

        function updateDateRange() {
            var sdate = new Date($('#sYear').val(), parseInt($('#sMonth').val() - 1), $('#sDay').val());
            var edate = new Date($('#eYear').val(), parseInt($('#eMonth').val() - 1), $('#eDay').val());
            $('#sDay').val(sdate.getDate());
            $('#sMonth').val(parseInt(sdate.getMonth() + 1));
            $('#sYear').val(sdate.getFullYear());
            $('#eDay').val(edate.getDate());
            $('#eMonth').val(parseInt(edate.getMonth() + 1));
            $('#eYear').val(edate.getFullYear());
        }

        validateForm();
    });
</script>