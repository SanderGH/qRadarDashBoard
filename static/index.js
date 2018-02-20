/*function openCity(evt, cityName) {
    // Declare all variables
    var i, tabcontent, tablinks;

    // Get all elements with class="tabcontent" and hide them
    tabcontent = document.getElementsByClassName("tabcontent");
    for (i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "none";
    }

    // Get all elements with class="tablinks" and remove the class "active"
    tablinks = document.getElementsByClassName("tablinks");
    for (i = 0; i < tablinks.length; i++) {
        tablinks[i].className = tablinks[i].className.replace(" active", "");
    }

    // Show the current tab, and add an "active" class to the link that opened the tab
    document.getElementById(cityName).style.display = "block";
    evt.currentTarget.className += " active";
}
document.getElementById("defaultOpen").click();*/

// model
//var monthNames = ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",  "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"];
function dateDiff( date2, date1 ) {
    date1 = new Date( date1 );
    date2 = new Date( date2 );
    var milliseconds = date2.getMilliseconds() - date1.getMilliseconds();

    if ( milliseconds < 0 ) {
        milliseconds += 1000;
        date2.setSeconds( date2.getSeconds() - 1 );
    }

    var seconds = date2.getSeconds() - date1.getSeconds();
    if ( seconds < 0 ) {
        seconds += 60;
        date2.setMinutes( date2.getMinutes() - 1 );
    }

    var minutes = date2.getMinutes() - date1.getMinutes();
    if ( minutes < 0 ) {
        minutes += 60;
        date2.setHours( date2.getHours() - 1 );
    }

    var hours = date2.getHours() - date1.getHours();
    if ( hours < 0 ) {
        hours += 24;
        date2.setDate( date2.getDate() - 1 );
    }

    var days = date2.getDate() - date1.getDate();
    if ( days < 0 ) {
        days += new Date( date2.getFullYear(), date2.getMonth() - 1, 0 ).getDate() + 1;
        date2.setMonth( date2.getMonth() - 1 );
    }

    var months = date2.getMonth() - date1.getMonth();
    if ( months < 0 ) {
        months += 12;
        date2.setFullYear( date2.getFullYear() - 1 );
    }

    var years = date2.getFullYear() - date1.getFullYear();
    return "" + days + "d " + hours + "h " + minutes + "m " + seconds + "s";        
    //return [ years, months, days, hours, minutes, seconds, milliseconds ];
}

//offenses =  _.map( offenses, function(value, key) {
offenses =  _.map( JSON.parse(offenses), function(value, key) {
    var elapsed  = 0;
    var sElapsed = ""
    if( value.assigned_to != null && value.close_time == null )
    {
        elapsed = new Date() - new Date( value.start_time );
        sElapsed = dateDiff( new Date(), new Date( value.start_time )  );
    }

    if( value.closing_user != null && value.close_time != null )
    {
        elapsed = new Date(value.close_time) - new Date( value.start_time );
        sElapsed = dateDiff(  new Date(value.close_time), new Date( value.start_time ) );        
    }

    return {
        id: value.id,
        status: value.status,                        
        user_id: value.user_id,
        domain_id: value.domain_id,
        offense_source: value.offense_source,
        rules: value.rules,        
        severity: value.severity,
        event_count: value.event_count,        
        assigned_to: value.assigned_to,        
        closing_user: value.closing_user,        
        source_addresses: value.source_addresses,
        local_destination_address_ids: value.local_destination_address_ids,
        start_time: value.start_time,        
        last_updated_time: value.last_updated_time,        
        close_time: value.close_time,                
        elapsed_time: elapsed,
        elapsed_str: sElapsed
    };
} );

regPieChart = [];
ko.bindingHandlers.regBarBind = {
    init: function (element, valueAccessor, allBindings, viewModel, bindingContext) {
        var data = ko.unwrap(valueAccessor());

        var ctx = document.getElementById(element.id);
        regPieChart[element.id] = new Chart( ctx, {
            type: 'pie',

            // The data for our dataset
            data: {
                datasets: [{
                    backgroundColor: [
                        'rgb(255, 99, 132)',
                        'rgb(54, 162, 235)',
                        'rgb(255, 206, 86)',
                        'rgb(75, 192, 192)',
                        'rgb(153, 102, 255)',
                        'rgb(255, 159, 64)'
                    ],
                    //borderColor: 'rgb(255, 99, 132)',
                }]
            },
            options: {
                title: {
                    display: true,
                    text: element.title
                },
                legend: {
                    position: "right"
                },
                responsive: true
            }            
        });
    },
    update: function (element, valueAccessor, allBindings, viewModel, bindingContext) {
        var data1 = ko.unwrap( valueAccessor());
        var data = _.filter( data1 , function(offense){
            return ( new Date() - new Date( offense.start_time ) ) <= 480*60*60*1000
        })

        severities = ( _.map( _.groupBy( data, 'severity' ),
            function(value, key){  
                return { 'severity' : key, 'count' : value.length};
            }
        ));
    
        regPieChart[element.id].data.labels = _.map(severities, 'severity');
        regPieChart[element.id].data.datasets[0].data = _.map(severities, 'count');
        regPieChart[element.id].update();
    }                        
}

// create viewModel
function ViewModel()
{
    var self = this;
    self.OffensesVM = new OffensesViewModel();
}

function OffensesViewModel()
{
    var self = this;

    self.logSources =  ko.observableArray(JSON.parse(sources));
    self.filteredOffenses = ko.observableArray(offenses);
    self.regOffenses = ko.observableArray( _.filter( offenses, function( offense ) {
        return ( offense.assigned_to == null && offense.close_time == null );
    }));
    self.assignOffenses = ko.observableArray( _.filter( offenses, function( offense ) {
        return ( offense.assigned_to != null && offense.close_time == null );
    }));
    self.closeOffenses = ko.observableArray( _.filter( offenses, function( offense ) {
        return ( offense.closing_user != null && offense.close_time != null );
    }));

    self.viewRegistered = ko.observable(true);
    self.changeViewRegistered = function(){
            self.filteredOffenses.removeAll();
            ddd = _.filter( offenses, function( offense ) {
                visible = false;
                if ( self.viewRegistered() && offense.assigned_to == null && offense.close_time == null )
                    visible = true;
                if( self.viewAssigned() && offense.assigned_to != null && offense.close_time == null )
                    visible = true;
                if ( self.viewClosed() && offense.closing_user != null && offense.close_time != null )
                    visible = true;

                return visible; 
            });
            _.forEach( ddd, function(value) {
                self.filteredOffenses.push(value);
            })
            //self.filteredOffenses = 
            //self.filteredOffenses.valueHasMutated();
    }

    self.IsShowAssigned = function(){
        return self.viewAssigned && self.assignOffenses().lenght>0
    }
    self.viewAssigned = ko.observable(true);
    self.viewClosed = ko.observable(true);
}

ViewModel = new ViewModel();
ko.applyBindings( ViewModel );