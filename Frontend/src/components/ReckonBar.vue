<template>
    <div id="reckonbarcontainer">

        <div id="filterbar" :class="{ invisible: scene.fetchData || !visible, visible: !scene.fetchData && visible }" class="container">
            <div class="row">
                <form class="col s12">
                    <div class="row">

                        <div id="typeselectorcontainer" class="input-field col s4 m2 l2 xl2 white-text" ref="myInput">
                            <select v-model="formData.type" v-on:change="validateForm()">
                                <option v-for="y in formOptions.type" :value="y" class="white-text">{{ y }}</option>
                            </select>
                            <label>Reckon type</label>
                        </div>

                        <div class="file-field input-field col s12 m10 l4 xl4">
                            <div class="waves-effect waves-light btn-small grey darken-2 filebutton">
                                <span>File</span>
                                <input id="file" type="file" v-on:change="validateForm()">
                            </div>
                            <div class="file-path-wrapper">
                                <input class="file-path validate" type="text">
                            </div>
                        </div>

                        <div class="input-field col s12 m9 l4 xl4" :class="{ invisible: formData.type !== '1 to 1', visible: formData.type === '1 to 1'}">
                            <i id="useridicon" class="large material-icons prefix grey-text">account_circle</i>
                            <input id="first_name" type="text" class="validate white-text" v-model="formData.userId" v-on:input="validateForm()">
                            <label for="first_name">User Id</label>
                        </div>

                        <div id="buttoncontainer" class="input-field col s4 m3 l2 xl2" ref="myInput">
                            <a id="reloadbutton"
                               :class="{ buttondisabled: !formData.validated}"
                               class="btn-large waves-effect waves-light purple darken-4 z-depth-3"
                               @click="reckon()">
                                <p class="white-text">Reckon</p>
                            </a>
                        </div>

                    </div>
                </form>
            </div>
        </div>

        <div id="operationprogresscontainer" :class="{ invisible: !scene.fetchData || !visible, visible: scene.fetchData && visible }" class="container">
            <div class="row">
                <div class="col s2 m2 l4 xl4"></div>
                <div id="operationprogresscontent" class="col s8 m8 l4 xl4 z-depth-3">
                    <div class="row titlerow">
                        <div class="col s12 m12 l12">
                            <h3 class="white-text">Reckon</h3>
                        </div>
                    </div>
                    <div class="row formrow">

                        <div class="messagecontainer" :class="{ invisible: !scene.operationProgress, visible: scene.operationProgress }">

                            <div class="messagecontainercontent" :class="{ invisible: !scene.operationProgress, visible: scene.operationProgress }">
                                <div class="white-text loading-text"> {{scene.operationProgressMessage}}</div>
                                <div class="preloader-wrapper small active">
                                    <div class="spinner-layer spinner-green-only">
                                        <div class="circle-clipper left">
                                            <div class="circle"></div>
                                        </div><div class="gap-patch">
                                        <div class="circle"></div>
                                    </div><div class="circle-clipper right">
                                        <div class="circle"></div>
                                    </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div class="errorcontainer" :class="{ invisible: !scene.error, visible: scene.error }">
                            <div class="errorcontainercontent">
                                <h4 class="white-text">Error</h4>
                                <p class="white-text">{{scene.errorMessage}}</p>
                            </div>
                        </div>

                        <div class="successcontainer" :class="{ invisible: !scene.success, visible: scene.success }">
                            <div class="successcontainercontent">
                                <h4 class="white-text">Success!</h4>
                                <p class="white-text">{{scene.successMessage}}</p>
                            </div>
                        </div>

                    </div>
                </div>
                <div class="col s2 m2 l4 xl4"></div>
            </div>
        </div>

    </div>


</template>


<script>

    import { RECKON_ENDPOINT_URL } from "../sensitivedata/aws";
    import { API_KEY } from "../sensitivedata/aws";

    export default {
        name: "reckon-bar",
        props: {
            callback: {},
            visible: {}
        },
        created() {
            this.formData.type = this.formOptions.type[0];
        },
        mounted() {
            M.FormSelect.init(document.querySelectorAll('select'));
            $("input.select-dropdown").css("color", "white");
        },
        data() {
            return {
                formData: {
                    userId: '',
                    type: '',
                    image: '',
                    validated: false
                },
                formOptions: {
                    type: ['1 to 1', '1 to N', 'N to N'],
                },
                reckonObject: {
                    id: '',
                    image: '',
                    device: 'Web admin client',
                    reason: 'Web client reckon request',
                    coordinates: {
                        lat: '',
                        lng:''
                    },
                },
                scene: {
                    fetchData: false,
                    operationProgress: false,
                    operationProgressMessage: 'Reckon ...',
                    error: false,
                    errorMessage: 'Error',
                    success: false,
                    successMessage: 'Success'
                }
            }
        },
        methods: {
            reckon: function () {
                this.scene.fetchData = true;
                this.scene.operationProgress = true;
                this.scene.operationProgressMessage = 'Reckon: encoding image...';
                var file = document.querySelector('#file').files[0];
                var reader = new FileReader();
                reader.readAsDataURL(file);
                reader.onload = () => {
                    try {
                        this.formData.image = reader.result.split(";")[1].replace('base64,', '');
                        this.getGeolocation();
                    }
                    catch(err) {
                        this.showError(String(err))
                        return
                    }
                };
                reader.onerror = function (error) {
                    this.showError(String(error))
                };
            },
            getGeolocation: function () {
                this.scene.operationProgressMessage = 'Reckon: acquiring coordinates...';
                if (navigator.geolocation) {
                    navigator.geolocation.getCurrentPosition(this.updateGeolocationOnRegistrationObject);
                } else {
                    this.showError("Unable to get browser's coordinates.");
                }
            },
            updateGeolocationOnRegistrationObject: function (position) {
                this.reckonObject.coordinates.lat = String(position.coords.latitude)
                this.reckonObject.coordinates.lng = String(position.coords.longitude)
                this.buildRegistrationObject();
            },
            buildRegistrationObject: function () {
                this.scene.operationProgressMessage = 'Reckon: requesting...';
                this.reckonObject.reason = 'Web client reckon request';
                this.reckonObject.id = this.formData.userId;
                this.reckonObject.image = this.formData.image;

                fetch(RECKON_ENDPOINT_URL, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'x-api-key': API_KEY
                    },
                    body: JSON.stringify(this.reckonObject)
                })
                    .then(response => response.json())
                    .then(data => {
                        console.log(data);
                        if (data.op_status && data.op_status == 'success')
                            this.showSuccess(data.message);
                        else if (data.op_status && data.op_status == 'failed' && data.message)
                            this.showError(data.message);
                        else
                            this.showError('Registration error!')
                    })
                    .catch(err => {
                        console.log(err);
                        this.showError('Fetch error: ' + String(err));
                    })
            },
            validateForm: function () {
                if (this.formData.userId === '' && this.formData.type === '1 to 1') {
                    this.formData.validated = false;
                    return;
                }
                if (!document.querySelector('#file').files[0]) {
                    this.formData.validated = false;
                    return;
                }
                this.formData.validated = true;
            },
            showError: function (msg) {
                this.scene.errorMessage = msg;
                this.scene.operationProgress = false;
                this.scene.error = true;
                setTimeout(() => {
                    this.scene.fetchData = false;
                }, 2000)
                setTimeout(() => {
                    this.scene.error = false;
                    this.scene.success = false;
                }, 2300)
            },
            showSuccess: function (msg) {
                this.scene.successMessage = msg;
                this.scene.operationProgress = false;
                this.scene.success = true;
                setTimeout(() => {
                    this.scene.fetchData = false;
                }, 3000)
                setTimeout(() => {
                    this.scene.error = false;
                    this.scene.success = false;
                }, 3300)
            },
        }
    }
</script>


<style scoped>

    #filterbar {
        background-color: rgba(69, 90, 100, 0.4);
        margin-bottom: 20px;
        border-radius: 0.25rem;
    }

    #typeselectorcontainer {
        margin-right: 0em;
    }

    #buttoncontainer{
        height: 100%;
        padding-right: 1.3em;
        text-align: right;
        margin-top: 18px !important;
    }

    #operationprogresscontainer {
        position: absolute;
        left: 50%;
        transform: translate(-50%);
        top: 20px;
    }

    #operationprogresscontent {
        background-color: rgba(255, 255, 255, 0.1);
        border-radius: 0.25rem;
    }

    .messagecontainer, .errorcontainer, .successcontainer {
        position: absolute;
        top: 72px;
        bottom: 7px;
        left: 7px;
        right: 7px;
        border-radius: 0.25rem;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .messagecontainer {
        background-color: rgba(255,255,255, 0.1);
    }

    .errorcontainer {
        background-color: rgba(220,20,60, 0.5);
    }

    .successcontainer {
        background-color: rgba(113, 220, 194, 0.5);
    }

    .messagecontainercontent,  .errorcontainercontent, .successcontainercontent{
        text-align: center;
    }

    .messagecontainercontent {
        animation: fadeInOut6 1s ease reverse forwards infinite
    }


    .titlerow {
        background-color: rgba(255, 255, 255, 0.1);
        padding: 15px 10px 10px 10px;
    }

    .formrow {
        height: 250px;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .loading-text {
        margin-bottom: 10px;
    }

    .buttondisabled {
        opacity: 0.2;
        pointer-events: none
    }

    @-moz-keyframes spin { 100% { opacity:0; } }
    @-webkit-keyframes spin { 100% { opacity:0; } }
    @keyframes spin { 100% { opacity:0; } }

    @keyframes fadeInOut6 {
        0% { opacity: 0.4 }
        50% { opacity: 0.8 }
        100% { opacity: 0.4 }
    }

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