<template>

    <div class="content">

        <filter-bar :isLoading="isLoading"
                    :callback="loadData"
                    :visible="!entryMode.active"
        />

        <log-cards-container :data="reckonData"
                             :bucketUrl="bucket_url"
                             :callback="selectEntry"
                             :visible="!entryMode.active"

        />

        <entry-mode-container :data="entryMode.data"
                              :bucketUrl="bucket_url"
                              :callback="setEntryModeInactive"
                              :visible="entryMode.active"
        />

    </div>

</template>

<script>

    import FilterBar from '@/components/FilterBar.vue'
    import LogCardsContainer from '@/components/LogCardsContainer.vue'
    import EntryModeContainer from '@/components/EntryModeContainer.vue'
    import { ADMIN_ENDPOINT_URL } from "../sensitivedata/aws";
    import { BUCKET_URL } from "../sensitivedata/aws";
    import { API_KEY } from "../sensitivedata/aws";

    export default {
        name: "log-fail-reckon",
        components: {
            FilterBar,
            LogCardsContainer,
            EntryModeContainer
        },
        data() {
            return {
                bucket_url: BUCKET_URL,
                isLoading: false,
                reckonData: [],
                entryMode: {
                    active: false,
                    data: {}
                }
            }
        },
        methods: {
            loadData: function (request) {
                this.isLoading = true;
                this.reckonData = [];
                request.command = 'get';
                request.table = 'reckon-fail';
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
                        this.reckonData = data.payload;
                        this.isLoading = false;
                    })
                    .catch(err => {
                        console.error('Failed retrieving data : ' + err);
                        this.isLoading = false;
                    })
            },
            selectEntry: function (entry) {
                this.entryMode.data = entry;
                this.entryMode.active = true;
                window.scrollTo(0, 0);
            },
            setEntryModeInactive() {
                this.entryMode.active = false;
            }
        }
    }

</script>


<style scoped>

    @media only screen and (max-width: 575px) {
        .content {
            margin-top: 20px;
            padding-bottom: 50px;
            margin-left: auto;
            margin-right: auto;
            width: 90%;
        }
    }

    @media only screen and (min-width: 576px) {
        .content {
            margin-top: 20px;
            padding-bottom: 50px;
            width: 100%;
        }
    }

</style>
