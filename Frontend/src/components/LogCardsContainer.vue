<template>

    <div id="cardscontainer" class="container" :class="{ invisible: !visible, visible: visible }" v-if="dataInner.length">
<!--        <p class="white-text">{{this.isMobile}}</p>-->
        <div class="card evcard z-depth-3" v-for="reckon in computedData">

            <div class="card-image" @click="callback(reckon)"   >
                <div class="imagecontainer">
<!--                    <img v-if="isMobile"-->
<!--                         class="log-image mobileimage"-->
<!--                         :src="bucketUrl + reckon.img_info.s3_path_hash"-->
<!--                         alt="Identity entry"-->
<!--                         v-bind:style="{-->
<!--                            transform: 'translate(-' + translationX(reckon)*100 + '%, -' + translationY(reckon)*100 + '%) rotate(' + rotation(reckon) + 'deg)'}">-->
                    <img v-if="checkOrientation(reckon)"
                         class="log-image highimage"
                         :src="bucketUrl + reckon.img_info.s3_path_hash"
                         alt="Identity entry"
                         v-bind:style="{
                            transform: 'translate(-' + translationX(reckon)*100 + '%, -' + translationY(reckon)*100 + '%)'}">
                    <img v-else
                         class="log-image wideimage"
                         :src="bucketUrl + reckon.img_info.s3_path_hash"
                         alt="Identity entry"
                         />
                </div>
                <div class="imgcaption">
                    <div class="left">
                        {{ getDateFromDateTime(reckon.time) }}
                    </div>
                    <div class="right">
                        {{ getTimeFromDateTime(reckon.time) }}
                    </div>
                </div>
            </div>

            <div class="card-content white-text">
                <p class="card-text truncate">{{ reckon.userId }}</p>
<!--                <p class="card-text truncate">{{ reckon.img_info.img_meta_data.exif.Orientation ?  reckon.img_info.img_meta_data.exif.Orientation : 'None'}}</p>-->
            </div>

        </div>

        <div class="paginationcontainer">
            <div class="paginationbuttonleft waves-effect waves-light" @click="changePage(-1)">
                <i class="tiny material-icons white-text">keyboard_arrow_left</i>
            </div>
            <div class="paginationbuttonright waves-effect waves-light" @click="changePage(1)">
                <i class="tiny material-icons white-text">keyboard_arrow_right</i>
            </div>
            <div class="spacer hide-on-med-and-up"></div>
            <small class="white-text paginationcaption">Items {{displayLimits.start}}-{{displayLimits.start+displayLimits.limit-1}} of {{dataInner.length}}</small>

        </div>

    </div>

</template>

<script>
    export default {
        name: "log-cards-container",
        props: {
            data: {},
            bucketUrl: {},
            callback: {},
            visible: {}
        },
        data() {
            return {
                dataInner: [],
                isMobile: false,
                displayLimits: {
                    limit: 14,
                    start: 0,
                }
            }
        },
        mounted() {
            if(/(android|bb\d+|meego).+mobile|avantgo|bada\/|blackberry|blazer|compal|elaine|fennec|hiptop|iemobile|ip(hone|od)|ipad|iris|kindle|Android|Silk|lge |maemo|midp|mmp|netfront|opera m(ob|in)i|palm( os)?|phone|p(ixi|re)\/|plucker|pocket|psp|series(4|6)0|symbian|treo|up\.(browser|link)|vodafone|wap|windows (ce|phone)|xda|xiino/i.test(navigator.userAgent)
                || /1207|6310|6590|3gso|4thp|50[1-6]i|770s|802s|a wa|abac|ac(er|oo|s\-)|ai(ko|rn)|al(av|ca|co)|amoi|an(ex|ny|yw)|aptu|ar(ch|go)|as(te|us)|attw|au(di|\-m|r |s )|avan|be(ck|ll|nq)|bi(lb|rd)|bl(ac|az)|br(e|v)w|bumb|bw\-(n|u)|c55\/|capi|ccwa|cdm\-|cell|chtm|cldc|cmd\-|co(mp|nd)|craw|da(it|ll|ng)|dbte|dc\-s|devi|dica|dmob|do(c|p)o|ds(12|\-d)|el(49|ai)|em(l2|ul)|er(ic|k0)|esl8|ez([4-7]0|os|wa|ze)|fetc|fly(\-|_)|g1 u|g560|gene|gf\-5|g\-mo|go(\.w|od)|gr(ad|un)|haie|hcit|hd\-(m|p|t)|hei\-|hi(pt|ta)|hp( i|ip)|hs\-c|ht(c(\-| |_|a|g|p|s|t)|tp)|hu(aw|tc)|i\-(20|go|ma)|i230|iac( |\-|\/)|ibro|idea|ig01|ikom|im1k|inno|ipaq|iris|ja(t|v)a|jbro|jemu|jigs|kddi|keji|kgt( |\/)|klon|kpt |kwc\-|kyo(c|k)|le(no|xi)|lg( g|\/(k|l|u)|50|54|\-[a-w])|libw|lynx|m1\-w|m3ga|m50\/|ma(te|ui|xo)|mc(01|21|ca)|m\-cr|me(rc|ri)|mi(o8|oa|ts)|mmef|mo(01|02|bi|de|do|t(\-| |o|v)|zz)|mt(50|p1|v )|mwbp|mywa|n10[0-2]|n20[2-3]|n30(0|2)|n50(0|2|5)|n7(0(0|1)|10)|ne((c|m)\-|on|tf|wf|wg|wt)|nok(6|i)|nzph|o2im|op(ti|wv)|oran|owg1|p800|pan(a|d|t)|pdxg|pg(13|\-([1-8]|c))|phil|pire|pl(ay|uc)|pn\-2|po(ck|rt|se)|prox|psio|pt\-g|qa\-a|qc(07|12|21|32|60|\-[2-7]|i\-)|qtek|r380|r600|raks|rim9|ro(ve|zo)|s55\/|sa(ge|ma|mm|ms|ny|va)|sc(01|h\-|oo|p\-)|sdk\/|se(c(\-|0|1)|47|mc|nd|ri)|sgh\-|shar|sie(\-|m)|sk\-0|sl(45|id)|sm(al|ar|b3|it|t5)|so(ft|ny)|sp(01|h\-|v\-|v )|sy(01|mb)|t2(18|50)|t6(00|10|18)|ta(gt|lk)|tcl\-|tdg\-|tel(i|m)|tim\-|t\-mo|to(pl|sh)|ts(70|m\-|m3|m5)|tx\-9|up(\.b|g1|si)|utst|v400|v750|veri|vi(rg|te)|vk(40|5[0-3]|\-v)|vm40|voda|vulc|vx(52|53|60|61|70|80|81|83|85|98)|w3c(\-| )|webc|whit|wi(g |nc|nw)|wmlb|wonu|x700|yas\-|your|zeto|zte\-/i.test(navigator.userAgent.substr(0,4))) {
                this.isMobile = true;
            }
        },
        methods: {
            changePage: function (move) {
                if (move>0) {
                    let newStart = this.displayLimits.start + this.displayLimits.limit;
                    if (newStart>= this.dataInner.length) {
                        this.displayLimits.start = 0;
                    }
                    else {
                        this.displayLimits.start = newStart;
                    }
                }
                else if (move<0) {
                    if (this.dataInner.length === this.displayLimits.limit) return;
                    let newStart = this.displayLimits.start - this.displayLimits.limit;
                    if (newStart<0) {
                        this.displayLimits.start = (this.dataInner.length)-this.dataInner.length%this.displayLimits.limit;
                    }
                    else {
                        this.displayLimits.start = newStart;
                    }
                }
                this.runCascadeEffectShow();
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
            runCascadeEffectShow: function() {
                this.dataInner = this.data;
                // this.imageSkew();
                setTimeout(() => {
                    var elems = $('#cardscontainer').children();
                    $(elems).each(function(index) {
                        $(this).delay(50*index).animate({opacity: 1}, 200);
                    });
                }, 100);
            },
            runCascadeEffectHide: function() {
                setTimeout(() => {
                    var elems = $('#cardscontainer').children();
                    $(elems).each(function(index) {
                        $(this).delay(50*index).animate({opacity: 0}, 200);
                    });
                }, 100);

            },
            checkOrientation: function(item) {
                return item.img_info.img_meta_data.dimensions.height>item.img_info.img_meta_data.dimensions.width;
            },
            translationX: function (item) {
                return 0;
            },
            translationY: function (item) {
                return (item.bounding_box.Top/2);
            },
            rotation: function(item) {
                if (!this.isMobile) return;
                var exifOrientation = item.img_info.img_meta_data.exif.Orientation;
                if (exifOrientation === 3 || exifOrientation === 4) return 180;
                else if (exifOrientation === 5 || exifOrientation === 6) return -90;
                else if (exifOrientation === 7 || exifOrientation === 8) return 90;
                return 0;
            },
        },

        computed: {
            computedData(){
                return this.dataInner.slice(this.displayLimits.start, this.displayLimits.start+this.displayLimits.limit);
            }
        },
        watch: {
            data: function (val) {
                if (this.data.length !== 0) {
                    this.runCascadeEffectShow();
                }
                else {
                    this.runCascadeEffectHide();
                    this.displayLimits.start = 0;
                }
            }
        }
    }
</script>

<style scoped>

    #cardscontainer{
        position: relative;
        text-align: center;
        z-index: 100;
        background-color: rgba(255, 255, 255, 0.1);
        border-radius: 0.25em 0em 0.25em 0.25em;
        margin-top: 40px;
        padding-top: 13px;
        padding-bottom: 7px;
    }

    #cardscontainer .card-content {
        padding: 5px !important;
    }

    @media only screen and (max-width: 575px) {
        .paginationcontainer{
            height: 40px !important;
            top: -40px !important;
        }
        .paginationcaption {
            margin: 0px !important;
            padding: 0px !important;
        }
        #cardscontainer{
            margin-top: 60px !important;
        }

        .paginationbuttonleft, .paginationbuttonright{
            padding-top: 10px !important;
        }
    }

    @media only screen and (min-width: 576px) {

    }

    .spacer {
        height: 10px;
        width: 10px;
        margin: auto;
    }

    .paginationcontainer{
        position: absolute;
        top: -20px;
        right: 0px;
        background-color: rgba(255, 255, 255, 0.1);
        border-radius: 0.25em 0.25em 0em 0em;
        width: 210px;
        height: 20px;
    }

    .paginationbuttonleft, .paginationbuttonright{
        background-color: rgba(255, 255, 255, 0.05);
        height: 100%;
        width: 40px;
        padding-top: 2px;
    }

    .paginationbuttonleft:hover, .paginationbuttonright:hover{
        background-color: rgba(255, 255, 255, 0.2);
    }

    .paginationbuttonleft{
        border-radius: 0.25em 0em 0em 0em;
        float: left;
    }

    .paginationbuttonright{
        border-radius: 0em 0.25em 0em 0em;
        float: right;
    }

    .imgcaption {
        position: absolute;
        bottom: 0px;
        width: 100%;
        height: 20px;
        background-color: rgba(0,0,0,0.6);
        color: white;
        font-size: 0.7rem;
        text-align: center;
        padding: 3px;
    }

    .evcard {
        width: 10rem;
        display: inline-block;
        margin-right: 5px;
        margin-bottom: 5px;
        background: rgba(250,250,250,0.1);
        margin-top: 0px !important;
        cursor: pointer;
        transition: all 0.2s ease;
        opacity: 0;
    }

    .evcard:hover {
        transform: scale(1.01);
        background: rgba(250,250,250,0.15);
    }

    .imagecontainer{
        position:relative;
        overflow: hidden;
        height: 150px;
        width: 100%;
        /*background-color: white;*/
    }

    .log-image {
        position: absolute;
        /*object-fit: cover;*/
    }

    /*.mobileimage {*/
    /*    display: flex;*/
    /*    align-content: center;*/
    /*    width:100%;*/
    /*    height: auto;*/
    /*}*/

    .highimage {
        max-width:100%;
        height:auto;
    }

    .wideimage {
        width:auto !important;
        height: 100%;
    }

    .card .content small {
        display: inline-block !important;

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