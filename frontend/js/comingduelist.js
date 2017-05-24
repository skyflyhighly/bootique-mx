/*
 * Coming Due List
 */

function ComingDueList(options) {
    this.options = options;
    this.$table = $(options.listSelector);
    this.anchorDate = new Date();

    this.init();
    this.refresh();
}

ComingDueList.prototype.setActualHobbsForm = function(form) {
    this.actualHobbsForm = form;
}

ComingDueList.prototype.setNextDueHobbsForm = function(form) {
    this.nextDueHobbsForm = form;
}

ComingDueList.prototype.formatHobbsDate = function(date) {
    var dateString = '';
    var weekdays = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
    dateString += (date.getMonth() + 1) + '/'
    dateString += date.getDate() + '/';
    dateString += date.getFullYear() + ' ';
    dateString += weekdays[date.getDay()];
    return dateString;
}

ComingDueList.prototype.firstWeekDay = function() {
    var date = new Date(this.anchorDate.getTime());
    date.setDate(date.getDate() - date.getDay());
    return date;
}

ComingDueList.prototype.changeAnchorDate = function(date) {
    this.anchorDate = date;
    this.refresh();
}

ComingDueList.prototype.refresh = function() {
    var self = this;

    var data = {
        csrfmiddlewaretoken: self.options.apiCSRFToken,
        tail_id: self.options.tailId,
        start: self.firstWeekDay().toISOString(),
        days: 7,
    };
    $.ajax({
        url: self.options.comingDueListAPI,
        method: 'POST',
        data: data,
    })
    .then(function(response) {
        if (response.success) {
            self.$table.empty();

            var $thead = $('<thead />');
            $thead.append('<th><strong>Date</strong></th>');
            $thead.append('<th><strong>Flight</strong></th>');
            $thead.append('<th><strong>Hobbs<br>EOD</strong></th>');
            $thead.append('<th><strong>Next Due<br>Hobbs</strong></th>');
            $thead.append('<th><strong>Hobbs<br>Left</strong></th>');
            if (self.options.writeable) {
                $thead.append('<th />');
            }
            self.$table.append($thead);

            var lastDay = '';
            for (var hobbs of response.hobbs_list) {
                var $tr = $('<tr data-actual-hobbs-id="' + hobbs.actual_hobbs_id + '" data-next-due-hobbs-id="' + hobbs.next_due_hobbs_id + '" />');
                if (hobbs.day != lastDay) {
                    $tr.append('<td>' + self.formatHobbsDate(new Date(hobbs.day)) + '</td>');
                    lastDay = hobbs.day;
                } else {
                    $tr.append('<td></td>');
                }
                $tr.append('<td>' + hobbs.flight + '</td>');
                $tr.append('<td>' + hobbs.actual.toFixed(1) + '</td>');
                $tr.append('<td>' + hobbs.next_due.toFixed(1) + '</td>');
                $tr.append('<td>' + (hobbs.next_due - hobbs.actual).toFixed(1) + '</td>');
                if (self.options.writeable && hobbs.actual_hobbs_id) {
                    $tr.append('<td style="padding-bottom: 3px;">' +
                        '<a href="javascript:;" class="btn btn-primary btn-xs btn-edit-hobbs"><i class="fa fa-fw fa-edit"></i></a> ' +
                        '<a href="javascript:;" class="btn-delete-flight btn btn-danger btn-xs btn-delete-hobbs"><i class="fa fa-fw fa-trash"></i></a>' +
                        '</td>');
                }
                self.$table.append($tr);
            }
        }
    });
}

ComingDueList.prototype.init = function() {
    var self = this;

    self.$table.on('click', '.btn-edit-hobbs', function(e) {
        e.preventDefault();
        var $tr = $(this).closest('tr');
        if (self.actualHobbsForm) {
            var actualHobbsId = $tr.data('actual-hobbs-id');
            self.actualHobbsForm.load(actualHobbsId);
        }
        if (self.nextDueHobbsForm) {
            var actualHobbsId = $tr.data('next-due-hobbs-id');
            self.nextDueHobbsForm.load(actualHobbsId);
        }
    });

    self.$table.on('click', '.btn-delete-hobbs', function(e) {
        e.preventDefault();
        var $tr = $(this).closest('tr');
        var actualHobbsId = $tr.data('actual-hobbs-id');
        if (actualHobbsId) {
            var apiUrl = self.options.deleteActualHobbsAPI.replace('0', actualHobbsId);

            $.ajax({
                method: 'POST',
                url: apiUrl,
                data: {
                    csrfmiddlewaretoken: self.options.apiCSRFToken,
                },
            })
            .then(function(response) {
                if (response.success) {
                    self.refresh();
                }
            });
        }
    });
}

window.ComingDueList = ComingDueList;

if (module && module.exports) {
    module.exports = ComingDueList;
}