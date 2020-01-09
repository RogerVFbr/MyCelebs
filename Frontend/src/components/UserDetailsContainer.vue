<template>

    <div id="entrymodecontainer"
         class="container"
         :class="{ invisible: !visible && !deleteConfirmation, visible: visible && !deleteConfirmation}">

        <div class="row" :class="{faded: deleteConfirmation}" v-if="Object.keys(data).length > 0">

            <div class="col s12 m4 l4 img-column">

                <div class="userpicturecontainer">
                    <img v-if="!imgVertical" class="horizontalImg" :src="bucketUrl + data.img_info.s3_path_hash" alt="User picture">
                    <img v-else class="verticalImg" :src="bucketUrl + data.img_info.s3_path_hash" alt="User picture">
                    <div id="boundingbox"></div>
                    <div id="loadingregisters" :class="{ invisible2: isRegistersLoaded, visible2: !isRegistersLoaded }">
                        <div class="white-text loading-text">Loading registers...</div>
                        <div class="progress">
                            <div class="indeterminate"></div>
                        </div>
                    </div>
                    <div id="imagecounter"
                         :class="{ invisible2: !isRegistersLoaded, visible2: isRegistersLoaded }">
                        <small class="white-text">{{ index+1 }} / {{userRegisters.length}}</small>
                    </div>
                </div>
                <div id="navigationbutton-left" :class="{ invisible2: !isRegistersLoaded, visible2: isRegistersLoaded }">
                    <i class="waves-effect waves-light small material-icons white-text hoverable" @click="changeIndex(-1)">keyboard_arrow_left</i>
                </div>
                <div id="navigationbutton-right" :class="{ invisible2: !isRegistersLoaded, visible2: isRegistersLoaded }">
                    <i class="waves-effect waves-light small material-icons white-text hoverable" @click="changeIndex(1)">keyboard_arrow_right</i>
                </div>
            </div>

            <div class="col s12 m2 l2 data-column-1">
                <small class="grey-text">User Id</small>
                <p class="card-text white-text">{{ data.userId }}</p>
                <small class="grey-text">Time (UTC)</small>
                <p class="card-text white-text">{{ getDateFromDateTime(data.time) }} {{ getTimeFromDateTime(data.time)}}</p>
                <small class="grey-text">API Key Profile Name</small>
                <p class="card-text white-text">{{ data.identity.apiKeyProfileName }}</p>
                <small class="grey-text">Device</small>
                <p class="card-text white-text">{{ data.identity.device }}</p>
                <small class="grey-text">Source IP</small>
                <p class="card-text white-text">{{ data.identity.sourceIp }}</p>
                <small class="grey-text">User Agent</small>
                <p class="card-text white-text truncate">{{ data.identity.userAgent }}</p>
                <!--                <a class="btn tooltipped" data-position="left" data-tooltip="I am a tooltip">Hover me!</a>-->
                <small class="grey-text">Reason</small>
                <p class="card-text white-text">{{ data.reason }}</p>
            </div>

            <div class="col s12 m2 l2 data-column-2">
                <small class="grey-text">Age Range</small>
                <p class="card-text white-text">{{ data.face_details.AgeRange.Low }} - {{ data.face_details.AgeRange.High }}</p>
                <small class="grey-text">Gender</small>
                <p class="card-text white-text">{{ data.face_details.Gender.Value }} ({{ parseFloat(data.face_details.Gender.Confidence).toFixed(2) }}%)</p>
                <small class="grey-text">Emotions</small>
                <div class="white-text" v-for="emotion in data.face_details.Emotions">
                    {{ emotion.Type.toLowerCase().replace(/^\w/, c => c.toUpperCase()) }} ({{ parseFloat(emotion.Confidence).toFixed(2) }}%)
                </div>
                <div class="spacing"></div>
                <small class="grey-text">API Metrics</small>
                <div class="white-text" v-for="metric in data.api_metrics">
                    {{ metric.key }}: {{ metric.value }}
                </div>
                <div class="spacing"></div>
                <small class="grey-text">Image Info</small>
                <div class="white-text">H: {{ data.img_info.img_meta_data.dimensions.height }} px | W: {{ data.img_info.img_meta_data.dimensions.width }} px</div>
                <div class="white-text">Size: {{ data.img_info.img_meta_data.size }} | Type: {{ data.img_info.img_meta_data.type }}</div>
            </div>

            <div class="col s12 m2 l2 map-column">

                <div id="coordinatesunavailable">
                    <div class="white-text loading-text" v-if="!mapRenderCondition">Coordinates<br/>unavailable.</div>
                </div>

                <div class="maploading" :class="{ invisible2: isIFrameLoaded, visible2: !isIFrameLoaded }" v-if="mapRenderCondition">
                    <div class="maploadingcontent">
                        <div class="white-text loading-text">Loading map...</div>
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

                <div class="gmap_canvas map-responsive" :class="{ invisible2: !isIFrameLoaded, visible2: isIFrameLoaded, buttondisabled: deleteConfirmation }" v-if="mapRenderCondition">
                    <div id="coordssource" class="white-text" v-if="data.identity.coordinates.source === 'exif'">Source: Exif</div>
                    <iframe height="100%"
                            width="100%"
                            id="gmap_canvas"
                            :src="'https://maps.google.com/maps?q=' + data.identity.coordinates.lat + '%2C%20' +  data.identity.coordinates.lng + '&t=k&z=19&ie=UTF8&iwloc=&output=embed'"
                            frameborder="0"
                            scrolling="no"
                            marginheight="0"
                            marginwidth="0"
                            @load="isIFrameLoaded = true">
                    </iframe>
                </div>

            </div>

        </div>

        <div class="row closebuttonrow" :class="{faded: deleteConfirmation}">

            <div class="col s10 m10 l10 xl10">
                <div v-if="showAdvancedControls && Object.keys(data).length > 0">
                    <button class="waves-effect waves-light btn-small teal darken-4 changeimagebutton"
                            :class="{buttondisabled: deleteConfirmation}"
                            type="submit"
                            @click="close()">
                        <i class="material-icons">exposure_plus_1</i>
                        <i class="material-icons">image</i>
                    </button>
                    <button class="waves-effect waves-light btn-small yellow darken-3 changeimagebutton"
                            :class="{buttondisabled: deleteConfirmation}"
                            type="submit"
                            @click="close()">
                        <i class="material-icons">exposure_minus_1</i>
                        <i class="material-icons">image</i>
                    </button>
                    <button class="waves-effect waves-light btn-small red darken-4"
                            :class="{buttondisabled: deleteConfirmation}"
                            type="submit"
                            @click="openDeleteConfirmationDialog">
                        <i class="material-icons">delete</i>
                        <i class="material-icons">account_circle</i>

                    </button>
                </div>
            </div>

            <div class="col s2 m2 l2 xl2">
                <button class="waves-effect waves-light btn-small blue darken-2 right hide-on-small-only" :class="{buttondisabled: deleteConfirmation}" type="submit" @click="close()">
                    Close
                    <i class="material-icons right">close</i>
                </button>
                <button class="waves-effect waves-light btn-small blue darken-2 right hide-on-med-and-up" :class="{buttondisabled: deleteConfirmation}" type="submit" @click="close()">
                    <i class="material-icons">close</i>
                </button>
                <div style="clear: both"></div>
            </div>
        </div>

        <delete-user-container
                :userId="data.userId"
                :onDeleteComplete="onDatabaseUpdate"
                :onClose="function() {deleteConfirmation = false}"
                :visible="deleteConfirmation"
        />

    </div>

</template>


<script>

    import DeleteUserContainer from '@/components/DeleteUserContainer.vue'
    import { ADMIN_ENDPOINT_URL } from "../sensitivedata/aws";
    import { API_KEY } from "../sensitivedata/aws";

    export default {
        name: "user-details-container",
        components: {
            DeleteUserContainer
        },
        props: {
            selection: {},
            bucketUrl: {},
            callback: {},
            onReloadRequest: {},
            visible: {},
            showAdvancedControls: {}
        },
        mounted() {
            M.Tooltip.init(document.querySelectorAll('.tooltipped'));
            M.Materialbox.init(document.querySelectorAll('.materialboxed'));
        },
        data() {
            return {
                isIFrameLoaded: false,
                isRegistersLoaded: false,
                deleteConfirmation: false,
                imgVertical: false,
                data: {},
                userRegisters: [],
                index: 0,
                exifOrientation: 0
            }
        },
        methods: {
            loadUserRegisters: function () {
                this.isRegistersLoaded = false;
                this.userRegisters = [];

                let request = {};
                request.command = 'collectionById';
                request.userId = this.data.userId;
                request.table = '';

                fetch(ADMIN_ENDPOINT_URL, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'x-api-key': API_KEY
                    },
                    body: JSON.stringify(request)
                })
                    .then(response => response.json())
                    .then(data => {
                        this.userRegisters = data.payload.reverse();
                        this.data = this.userRegisters[0];
                        this.index = 0;
                        this.isRegistersLoaded = true;
                    })
                    .catch(err => {
                        console.error('Failed retrieving data : ' + err);
                    })
            },
            changeIndex: function (change) {
                this.index += change;
                if (this.index<0) this.index = this.userRegisters.length-1;
                else if (this.index>this.userRegisters.length-1) this.index = 0;
                this.data = this.userRegisters[this.index];
                this.loadGoogleMapsIframe();
                this.acquireImageOrientation();
                this.setBoundingBoxPosition();
            },
            acquireImageOrientation: function() {
                let height = this.data.img_info.img_meta_data.dimensions.height;
                let width = this.data.img_info.img_meta_data.dimensions.width;
                if (height > width) this.imgVertical = true;
                else this.imgVertical = false;
                var exifOrientation = this.data.img_info.img_meta_data.exif.Orientation;
                if (exifOrientation) this.exifOrientation = exifOrientation;
            },
            loadGoogleMapsIframe: function () {
                if (this.data.identity.coordinates.lat == 'N.A.' || this.data.identity.coordinates.lng == 'N.A') return;
                this.isIFrameLoaded = false;
                $('#gmap_canvas').attr(
                    'src',
                    'https://maps.google.com/maps?q=' + this.data.identity.coordinates.lat + '%2C%20' +
                    this.data.identity.coordinates.lng + '&t=k&z=19&ie=UTF8&iwloc=&output=embed');
            },
            setBoundingBoxPosition: function () {
                setTimeout(() => {
                    $("#boundingbox").css({
                        "top": (this.data.bounding_box.Top*100).toString() + '%',
                        "left": (this.data.bounding_box.Left*100).toString() + '%',
                        "width": (this.data.bounding_box.Width*100).toString() + '%',
                        "height": (this.data.bounding_box.Height*100).toString() + '%',
                    });
                }, 100);
            },
            getDateFromDateTime: function (datetime) {
                datetime = datetime.split('-')
                if (datetime.length<3) return 'N.A.'
                datetime = datetime.slice(0, 3)
                return datetime[2] + '/' + datetime[1] + '/' + datetime[0]
            },
            getTimeFromDateTime: function (datetime) {
                datetime = datetime.split('-')
                if (datetime.length<6) return 'N.A.'
                datetime = datetime.slice(3, 7)
                return datetime[0] + ':' + datetime[1] + ':' + datetime[2]
            },
            openDeleteConfirmationDialog: function() {
                this.deleteConfirmation = true;
                window.scrollTo(0, 0);
            },
            close: function () {
                if (this.callback) this.callback();
                this.isRegistersLoaded = false;
                this.isIFrameLoaded = false;
                this.deleteConfirmation = false;
                window.scrollTo(0, 0);
            },
            onDatabaseUpdate: function () {
                if (this.callback) this.callback();
                if (this.onReloadRequest) this.onReloadRequest();
                this.isIFrameLoaded = false;
                this.deleteConfirmation = false;
            },

        },
        computed: {
            mapRenderCondition: function() {
                var returnBool = true;
                if ('source' in this.selection.identity.coordinates && this.selection.identity.coordinates.source === 'N.A.') {
                    returnBool = false;
                }
                else if ('source' in this.selection.identity.coordinates && this.selection.identity.coordinates.source === 'device') {
                    if (this.selection.identity.coordinates.lat === "-50.000" && this.selection.identity.coordinates.lng === "-23.0000") {
                        returnBool = false;
                    }
                }
                return returnBool;
            }
        },
        watch: {
            visible: function(val) {
                if (this.visible == false) return;
                this.data = this.selection;
                console.log(this.data);
                this.loadGoogleMapsIframe();
                this.acquireImageOrientation();
                this.setBoundingBoxPosition();
                this.loadUserRegisters()
            }
        }
    }
</script>


<style scoped>

    #entrymodecontainer {
        position: absolute;
        left: 50%;
        transform: translate(-50%);
        top: 20px;
        background-color: rgba(255, 255, 255, 0.1);
        border-radius: 0.25rem;
        padding-top: 12px;
    }

    @media only screen and (max-width: 575px) {
        #entrymodecontainer { width: 85%; }
        .userpicturecontainer { margin-bottom: 20px; }
        .data-column-1 { margin-bottom: 15px; }
        .data-column-2 { margin-bottom: 20px; }
        .map-column { margin-bottom: 20px; }
        .closebuttonrow {
            height: 70px !important;
        }
        .closebuttonrow button {
            width: 60px !important;
            height: 60px !important;
            padding: 1px 0px 0px 0px !important;
            border-radius: 0.5rem;
        }
    }

    @media only screen and (min-width: 576px) {

    }

    #entrymodecontainer img {
        border-radius: 0.25rem;
    }

    .horizontalImg{
        width: 100%;
    }

    .verticalImg{
        height: 400px;
    }

    .maploading {
        position: absolute;
        display: flex;
        float:right;
        align-items: center;
        justify-content: center;
        top: 0px;
        left: 10px;
        right: 10px;
        bottom: 10px;
        background-color: rgba(255, 255, 255, 0.1);
        border-radius: 0.25rem;
        z-index: -1;
    }

    .changeimagebutton {
        margin-right: 10px;
    }

    .maploadingcontent {
        text-align: center;
        animation: fadeInOut6 1s ease reverse forwards infinite
    }

    #coordinatesunavailable {
        position: absolute;
        display: flex;
        float:right;
        align-items: center;
        justify-content: center;
        top: 0px;
        left: 10px;
        right: 10px;
        bottom: 10px;
        background-color: rgba(255, 255, 255, 0.1);
        border-radius: 0.25rem;
        z-index: -1;
    }

    #coordssource {
        position: absolute;
        background-color: rgba(0, 0, 0, 0.5);
        top: 0px;
        right: 10px;
        font-size: 0.7em;
        padding: 0.3em;
    }

    @keyframes fadeInOut6 {
        0% { opacity: 0.4 }
        50% { opacity: 0.8 }
        100% { opacity: 0.4 }
    }

    .img-column {
        overflow: hidden;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .userpicturecontainer {
        position: relative;
        /*max-height: 400px;*/
    }

    #boundingbox {
        position: absolute;
        border: 2px dotted rgba(255, 255, 255, 0.5);
        border-radius: 0.25rem;
    }

    #loadingregisters {
        position: absolute;
        background-color: rgba(0, 0, 0, 0.5);
        bottom: 0px;
        width: 100%;
        text-align: center;
        padding-top: 5px;
        border-radius: 0rem 0rem 0.25rem 0.25rem;
    }

    #loadingregisters .progress {
        position: absolute;
        bottom: 0px;
        margin-bottom: 0px !important;
        height: 3px !important;
    }

    #imagecounter {
        position: absolute;
        background-color: rgba(0, 0, 0, 0.5);
        top: 5px;
        right: 5px;
        text-align: center;
        padding: 2px;
        border-radius: 0.25rem;
    }

    #navigationbutton-left, #navigationbutton-right {
        position: absolute;
        top: 50%;
        transform: translateY(-50%);
        height: 30px;
        width: 30px;
        background-color: rgba(0,0,0,0.5);
        border-radius: 0.25rem;
        cursor: pointer;
    }

    #navigationbutton-left{
        left: 10px;
    }

    #navigationbutton-right {
        right: 10px;
    }

    .loading-text {
        margin-bottom: 10px;
    }

    .closebuttonrow {
        border-top: 1px solid rgba(255, 255, 255, 0.2);
        padding-top: 9px;
        height: 42px;
    }

    .spacing {
        height: 17px;
    }

    .gmap_canvas {
        float:left;
        border-radius: 0.25rem;
        width:100%;
        overflow:hidden;
        height:400px;
    }

    .col {
        flex-basis: auto !important;
    }

    .row {
        margin-bottom:  10px;
    }

    .buttondisabled {
        opacity: 0.2;
        pointer-events: none
    }

    .visible {
        visibility: visible;
        opacity: 1;
        transition: visibility 0s linear 0s, opacity 0.35s linear;
    }

    .faded {
        visibility: visible;
        opacity: 0.05;
        transition: visibility 0s linear 0s, opacity 0.35s linear;
    }

    .invisible {
        visibility: hidden;
        opacity: 0;
        transition: visibility 0s linear 0.35s, opacity 0.35s linear;
    }

    .visible2 {
        /*visibility: visible;*/
        opacity: 1;
        transition: opacity 1s linear;

    }

    .invisible2 {
        /*visibility: hidden;*/
        opacity: 0;
        transition: opacity 0.2s linear;
    }

</style>