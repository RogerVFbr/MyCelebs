<template>

    <div id="entrymodecontainer"
         class="container"
         :class="{ invisible: !visible && !deleteConfirmation, visible: visible && !deleteConfirmation}"
         v-if="Object.keys(data).length > 0">

        <div class="row" :class="{faded: deleteConfirmation}">

            <div class="col s12 m4 l4 img-column">
                <div class="userpicturecontainer">
                    <img v-if="!imgVertical" class="horizontalImg" :src="bucketUrl + data.img_info.s3_path_hash" alt="User picture">
                    <img v-else class="verticalImg" :src="bucketUrl + data.img_info.s3_path_hash" alt="User picture">
                    <div id="boundingbox"></div>
                </div>
            </div>

            <div class="col s12 m2 l2 data-column-1 ">
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

            <div class="col s8 m8 l8 xl8">
                <div v-if="showAdvancedControls">
                    <button class="waves-effect waves-light btn-small yellow darken-3 changeimagebutton" :class="{buttondisabled: deleteConfirmation}" type="submit" @click="close()">Change image</button>
                    <button class="waves-effect waves-light btn-small red darken-4" :class="{buttondisabled: deleteConfirmation}" type="submit" @click="deleteConfirmation = true">Delete user</button>
                </div>
            </div>

            <div class="col s4 m4 l4 xl4">
                <button class="waves-effect waves-light btn-small blue darken-2 right" :class="{buttondisabled: deleteConfirmation}" type="submit" @click="close()">Close</button>
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

    export default {
        name: "entry-mode-container",
        components: {
            DeleteUserContainer
        },
        props: {
            data: {},
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
                deleteConfirmation: false,
                imgVertical: false
            }
        },
        methods: {
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
            close: function () {
                if (this.callback) this.callback();
                this.isIFrameLoaded = false;
                this.deleteConfirmation = false;
            },
            onDatabaseUpdate: function () {
                if (this.callback) this.callback();
                if (this.onReloadRequest) this.onReloadRequest();
                this.isIFrameLoaded = false;
                this.deleteConfirmation = false;
            }
        },
        computed: {
            mapRenderCondition: function() {
                var returnBool = true;
                if ('source' in this.data.identity.coordinates && this.data.identity.coordinates.source === 'N.A.') {
                    returnBool = false;
                }
                else if ('source' in this.data.identity.coordinates && this.data.identity.coordinates.source === 'device') {
                    if (this.data.identity.coordinates.lat === "-50.000" && this.data.identity.coordinates.lng === "-23.0000") {
                        returnBool = false;
                    }
                }
                return returnBool;
            }
        },
        watch: {
            visible: function(val) {
                if (this.visible == false) return;
                console.log(this.data);
                this.isIFrameLoaded = false;
                $('#gmap_canvas').attr(
                    'src',
                    'https://maps.google.com/maps?q=' + this.data.identity.coordinates.lat + '%2C%20' +
                    this.data.identity.coordinates.lng + '&t=k&z=19&ie=UTF8&iwloc=&output=embed');

                if (this.data.img_info.img_meta_data.dimensions.height >
                    this.data.img_info.img_meta_data.dimensions.width) {
                    this.imgVertical = true;
                }
                else {
                    this.imgVertical = false;
                }

                setTimeout(() => {
                    $("#boundingbox").css({
                        "top": (this.data.bounding_box.Top*100).toString() + '%',
                        "left": (this.data.bounding_box.Left*100).toString() + '%',
                        "width": (this.data.bounding_box.Width*100).toString() + '%',
                        "height": (this.data.bounding_box.Height*100).toString() + '%',
                    });
                }, 100)


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
        .img-column { margin-bottom: 20px; }
        .data-column-1 { margin-bottom: 15px; }
        .data-column-2 { margin-bottom: 20px; }
        .map-column { margin-bottom: 20px; }
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

    #boundingbox {
        position: absolute;
        border: 2px dotted rgba(255, 255, 255, 0.5);
        border-radius: 0.25rem;
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