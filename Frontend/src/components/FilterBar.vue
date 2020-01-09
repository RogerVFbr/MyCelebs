<template>
    <div id="filterbar" :class="{ invisible: !visible, visible: visible }" class="container">
        <div class="row">
            <form class="col s12">
                <div class="row">
                    <div class="input-field col s12 m4 l5 xl5">
                        <i id="useridicon" class="large material-icons prefix grey-text">account_circle</i>
                        <input id="first_name" type="text" class="validate white-text" v-model="apiFilters.userId">
                        <label for="first_name">User Id</label>
                    </div>
                    <div class="input-field col s4 m1 l1 xl1 white-text" ref="myInput">
                        <select v-model="apiFilters.year">
                            <option v-for="y in apiFilterOptions.year" :value="y" class="white-text">{{ y }}</option>
                        </select>
                        <label>Year</label>
                    </div>
                    <div class="input-field col s4 m1 l1 xl1" ref="myInput2">
                        <select v-model="apiFilters.month" @change="setMonthToAll()">
                            <option value="all" selected>All</option>
                            <option v-for="y in apiFilterOptions.month" :value="y" class="white-text">{{ y }}</option>
                        </select>
                        <label>Month</label>
                    </div>
                    <div class="input-field col s4 m1 l1 xl1" ref="myInput2" :class="{ disabledInput: apiFilters.month == 'all' }">
                        <select v-model="apiFilters.day" @change="setDayToAll()">
                            <option value="all" selected>All</option>
                            <option v-for="y in apiFilterOptions.day" :value="y" class="white-text">{{ y }}</option>
                        </select>
                        <label>Day</label>
                    </div>
                    <div class="input-field col s4 m1 l1 xl1" ref="myInput" :class="{ disabledInput: apiFilters.day == 'all' }">
                        <select v-model="apiFilters.hour" @change="setHourToAll()">
                            <option value="all" selected>All</option>
                            <option v-for="y in apiFilterOptions.hour" :value="y" class="white-text">{{ y }}</option>
                        </select>
                        <label>Hour</label>
                    </div>
                    <div class="input-field col s4 m1 l1 xl1" ref="myInput" :class="{ disabledInput: apiFilters.hour == 'all' }">
                        <select v-model="apiFilters.minute" @change="setMinuteToAll()">
                            <option value="all" selected>All</option>
                            <option v-for="y in apiFilterOptions.minuteSecond" :value="y" class="white-text">{{ y }}</option>
                        </select>
                        <label>Minute</label>
                    </div>
                    <div class="input-field col s4 m2 l1 xl1" ref="myInput">
                        <a id="reloadbutton" class="btn-floating btn-large waves-effect waves-light purple darken-4 z-depth-3" @click="retrieveFilterParameters()" v-if="!isLoading"><i class="material-icons">autorenew</i></a>
                        <a id="reloadbutton-rotate" class="btn-floating btn-large waves-effect waves-light purple darken-4 z-depth-3" v-else><i class="material-icons">autorenew</i></a>
                    </div>
                </div>
            </form>
        </div>
    </div>

</template>

<script>
    export default {
        name: "filter-bar",
        props: {
            isLoading: {},
            callback: {},
            visible: {}
        },
        created() {
            this.buildYearOptions();
            this.buildMonthOptions();
            this.buildDayOptions();
            this.buildHourOptions();
            this.buildMinuteSecondOptions();
        },
        mounted() {
            M.FormSelect.init(document.querySelectorAll('select'));
            $("input.select-dropdown").css("color", "white");
            this.retrieveFilterParameters();
        },
        data() {
            return {
                apiFilters: {
                    userId: '',
                    year: '',
                    month: '',
                    day: '',
                    hour: '',
                    minute: '',
                    second: '',
                    milli: ''
                },
                apiFilterOptions: {
                    year: [],
                    month: [],
                    day: [],
                    hour: [],
                    minuteSecond: [],
                }
            }
        },
        methods: {
            retrieveFilterParameters: function () {
                const request = {
                    userId: this.apiFilters.userId,
                    year: this.apiFilters.year,
                    month: this.apiFilters.month,
                    day: this.apiFilters.day,
                    hour: this.apiFilters.hour,
                    minute: this.apiFilters.minute,
                    second: this.apiFilters.second
                };
                this.callback(request);
            },
            buildYearOptions: function () {
                this.apiFilterOptions.year = [];
                let currentYear = new Date().getFullYear();
                this.apiFilters.year = currentYear;
                for (let x = currentYear; x>currentYear-10; x--) this.apiFilterOptions.year.push(x);
            },
            buildMonthOptions: function () {
                this.apiFilterOptions.month = [];
                let currentMonth = new Date().getMonth() + 1;
                this.apiFilters.month = currentMonth;
                for (let x = 1; x<=12; x++) this.apiFilterOptions.month.push(x);
            },
            buildDayOptions: function () {
                this.apiFilterOptions.day = [];
                this.apiFilters.day = 'all';
                for (let x = 1; x<=31; x++) this.apiFilterOptions.day.push(x);
            },
            buildHourOptions: function () {
                this.apiFilterOptions.hour = [];
                this.apiFilters.hour = 'all';
                for (let x = 0; x<=23; x++) this.apiFilterOptions.hour.push(x);
            },
            buildMinuteSecondOptions: function () {
                this.apiFilterOptions.minuteSecond = [];
                this.apiFilters.minuteSecond = 'all';
                for (let x = 0; x<=59; x++) this.apiFilterOptions.minuteSecond.push(x);
            },
            setYearToAll: function () {
                this.apiFilters.year = 'all'
                this.setMonthToAll()
            },
            setMonthToAll: function () {
                if (this.apiFilters.month != 'all') return;
                this.apiFilters.day = 'all';
                this.setDayToAll()
            },
            setDayToAll: function () {
                if (this.apiFilters.day != 'all') return;
                this.apiFilters.hour = 'all'
                this.setHourToAll()
            },
            setHourToAll: function () {
                if (this.apiFilters.hour != 'all') return;
                this.apiFilters.minute = 'all'
                this.setMinuteToAll()
            },
            setMinuteToAll: function () {
                if (this.apiFilters.minute != 'all') return;
                this.apiFilters.second = 'all'
                this.$forceUpdate()
            }
        }
    }
</script>

<style scoped>

    #filterbar {
        background-color: rgba(255, 255, 255, 0.1);
        margin-bottom: 20px;
        border-radius: 0.25rem;
    }

    #reloadbutton {
        margin-left: 5px;
        margin-top: -10px;
    }

    #reloadbutton-rotate {
        margin-left: 5px;
        margin-top: -10px;
        -webkit-animation:spin 4s linear infinite;
        -moz-animation:spin 4s linear infinite;
        animation:spin 1s linear infinite;
    }

    @-moz-keyframes spin { 100% { -moz-transform: rotate(360deg); } }
    @-webkit-keyframes spin { 100% { -webkit-transform: rotate(360deg); } }
    @keyframes spin { 100% { -webkit-transform: rotate(360deg); transform:rotate(360deg); } }

    .dropdown-content>li>a {
        color: white !important;
    }

    .col {
        flex-basis: auto !important;
    }

    .row {
        margin-bottom:  10px;
    }

    .disabledInput {
        opacity: 0.5;
        pointer-events:none;
    }

    .input-field {
        margin-top: 25px !important;
        margin-bottom: 0px !important;
    }

    /* label color */
    .input-field label {
        color: #fff;
        opacity: 0.5;
    }
    /* label focus color */
    .input-field input[type=text]:focus + label {
        color: #fff !important;
        opacity: 1;

    }
    /* label underline focus color */
    .input-field input[type=text]:focus {
        border-bottom: 1px solid white !important;
        box-shadow: 0 1px 0 0 black !important;
    }
    /* valid color */
    .input-field input[type=text].valid {
        border-bottom: 1px solid green;
        box-shadow: 0 1px 0 0 black;
    }
    /* invalid color */
    .input-field input[type=text].invalid {
        border-bottom: 1px solid red;
        box-shadow: 0 1px 0 0 black;
    }
    /* icon prefix focus color */
    .input-field .prefix.active {
        color: white !important;
        opacity: 1;
    }

    .visible {
        visibility: visible;
        opacity: 1;
        transition: visibility 0s linear 0s, opacity 0.35s linear;
    }

    .invisible {
        visibility: hidden;
        opacity: 0;
        transition: visibility 0s linear 0.35s, opacity 0.35s linear;
    }

</style>