<template>

    <div id="newusercontainer" class="container" :class="{ invisible: !visible, visible: visible }">

        <div class="row">

            <div class="col s2 m2 l4 xl4"></div>

            <div id="newusercontent" class="col s8 m8 l4 xl4">

                <div class="row titlerow">
                    <div class="col s12 m12 l12">
                        <h3 class="white-text">Register new user</h3>
                    </div>
                </div>

                <div class="row formrow">

                    <div class="input-field col s12 m12 l12 xl12" :class="{ invisible: errorContent.show || registerContent.show, visible: !errorContent.show && !registerContent.show}">
                        <input id="first_name" type="text" class="validate white-text" v-model="formData.userId" v-on:change="validateForm()">
                        <label for="first_name">New User Id</label>
                    </div>

                    <div class="input-field col s12 m12 l12 xl12" :class="{ invisible: errorContent.show || registerContent.show, visible: !errorContent.show && !registerContent.show }">
                        <input id="reason" type="text" class="validate white-text" v-model="formData.reason" v-on:change="validateForm()">
                        <label for="reason">Reason</label>
                    </div>

                    <div class="file-field input-field col s12 m12 l12 xl12" :class="{ invisible: errorContent.show || registerContent.show, visible: !errorContent.show && !registerContent.show }">
                        <div class="waves-effect waves-light btn-small grey darken-2 filebutton">
                            <span>File</span>
                            <input id="file" type="file" v-on:change="validateForm()">
                        </div>
                        <div class="file-path-wrapper">
                            <input class="file-path validate" type="text">
                        </div>
                    </div>

                    <div class="errorcontainer" :class="{ invisible: !errorContent.show, visible: errorContent.show }">
                        <div class="errorcontainercontent">
                            <h4 class="white-text">Error</h4>
                            <p class="white-text">{{errorContent.message}}</p>
                        </div>
                    </div>

                    <div class="messagecontainer" :class="{ invisible: !registerContent.show, visible: registerContent.show }">
                        <div class="messagecontainercontent">
                            <div class="white-text loading-text">{{ registerContent.message }}</div>
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

                </div>

                <div class="row buttonrow">

                    <div class="col s12 m12 l12">

                        <button class="waves-effect waves-light btn-small red darken-4 closebutton" type="submit" @click="close()"
                                :class="{ buttondisabled: registerContent.show || errorContent.show }">
                            Cancel
                            <i class="material-icons right">cancel</i>
                        </button>

                        <button class="waves-effect waves-light btn-small teal darken-4 registerbutton" type="submit" @click="register()"
                                :class="{ buttondisabled: !formData.validated || registerContent.show || errorContent.show}">
                            Register
                            <i class="material-icons right">send</i>
                        </button>

                    </div>

                </div>

            </div>

            <div class="col s2 m2 l4 xl4"></div>

        </div>

    </div>

</template>

<script>

    import { REGISTER_ENDPOINT_URL } from "../sensitivedata/aws";
    import { API_KEY } from "../sensitivedata/aws";

    export default {
        name: "new-user-container",
        props: {
            onSave: {},
            onClose: {},
            visible: {}
        },
        data () {
            return {
                registerContent: {
                    show: false,
                    message: 'Registering...'
                },
                isRegistering: false,
                isRegisterCompleted: false,
                errorContent: {
                    show: false,
                    message: 'Unable to decode.'
                },
                formData: {
                    userId: '',
                    reason: '',
                    image: '',
                    validated: false
                },
                registrationObject: {
                    id: '',
                    image: '',
                    device: 'Web admin client',
                    reason: '',
                    coordinates: {
                        lat: '',
                        lng:''
                    },
                }
            }
        },
        methods: {
            close: function () {
                this.onClose();
            },
            register: function () {
                this.registerContent.show = true;
                this.registerContent.message = 'Registering: encoding image...';
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
                this.registerContent.message = 'Registering: acquiring coordinates...';
                if (navigator.geolocation) {
                    navigator.geolocation.getCurrentPosition(this.updateGeolocationOnRegistrationObject);
                } else {
                    this.showError("Unable to get browser's coordinates.");
                }
            },
            updateGeolocationOnRegistrationObject: function (position) {
                this.registrationObject.coordinates.lat = String(position.coords.latitude)
                this.registrationObject.coordinates.lng = String(position.coords.longitude)
                this.buildRegistrationObject();
            },
            buildRegistrationObject: function () {
                this.registerContent.message = 'Registering: requesting...';
                this.registrationObject.reason = this.formData.reason;
                this.registrationObject.id = this.formData.userId;
                this.registrationObject.image = this.formData.image;

                fetch(REGISTER_ENDPOINT_URL, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'x-api-key': API_KEY
                    },
                    body: JSON.stringify(this.registrationObject)
                })
                    .then(response => response.json())
                    .then(data => {
                        console.log(data);
                        if (data.op_status && data.op_status == 'success')
                            this.showSuccess();
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
                if (this.formData.userId == '') {
                    this.formData.validated = false;
                    return;
                }
                if (this.formData.reason == '') {
                    this.formData.validated = false;
                    return;
                }
                if (!document.querySelector('#file').files[0]) {
                    this.formData.validated = false;
                    return;
                }
                this.formData.validated = true;
            },
            showSuccess: function () {
                this.registerContent.message = 'Registration successful!';
                setTimeout(() => {
                    this.onSave();
                    this.registerContent.show = false;
                    this.isRegistering = false;
                    this.registerContent.message = 'Registering...';
                }, 1500)
            },
            showError: function (msg) {
                this.registerContent.show = false;
                this.errorContent.show = true;
                this.errorContent.message = msg;
                setTimeout(() => {
                    this.errorContent.show = false;
                    this.registerContent.message = 'Registering...';
                }, 2000)
            }
        }
    }
</script>

<style scoped>

    #newusercontainer {
        position: absolute;
        left: 50%;
        transform: translate(-50%);
        top: 20px;
    }

    #newusercontent {
        background-color: rgba(255, 255, 255, 0.1);
        border-radius: 0.25rem;
    }

    .titlerow {
        background-color: rgba(255, 255, 255, 0.1);
        padding: 15px 10px 10px 10px;
    }

    .buttonrow {
        border-top: 1px solid rgba(255, 255, 255, 0.2);
        height: 42px;
    }

    .buttondisabled {
        opacity: 0.2;
        pointer-events: none
    }

    .errorcontainer {
        position: absolute;
        top: 72px;
        bottom: 60px;
        left: 7px;
        right: 7px;
        background-color: rgba(220,20,60, 0.5);
        border-radius: 0.25rem;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .errorcontainercontent, .messagecontainercontent {
        text-align: center;
    }

    .messagecontainer {
        position: absolute;
        top: 72px;
        bottom: 60px;
        left: 7px;
        right: 7px;
        background-color: rgba(255,255,255, 0.1);
        border-radius: 0.25rem;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .messagecontainercontent {
        text-align: center;
        animation: fadeInOut6 1s ease reverse forwards infinite
    }

    @keyframes fadeInOut6 {
        0% { opacity: 0.4 }
        50% { opacity: 0.8 }
        100% { opacity: 0.4 }
    }

    .loading-text {
        margin-bottom: 10px;
    }

    .filebutton {
        /*height: 30px !important;*/
        margin-top: 0.8rem;
        height: 2.2rem !important;
        line-height: 2rem !important;
    }

    .closebutton {
        position: absolute;
        top: 10px;
        left: 10px;
    }

    .registerbutton {
        position: absolute;
        top: 10px;
        right: 10px;
        transition: all 0.3s;
    }

    .col {
        flex-basis: auto !important;
    }

    .row {
        margin-bottom:  10px;
    }

    .input-field {
        /*margin-top: 25px !important;*/
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
        z-index: 10;
        transition: visibility 0s linear 0s, opacity 0.35s linear;
    }

    .invisible {
        visibility: hidden;
        opacity: 0;
        z-index: -10;
        transition: visibility 0s linear 0.35s, opacity 0.35s linear;
    }

</style>