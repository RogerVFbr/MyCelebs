<template>

    <div class="content">

        <filter-bar :isLoading="isLoading"
                    :callback="loadData"
                    :visible="!entryMode.active && !showNewUserContainer"
        />

        <log-cards-container :data="reckonData"
                             :bucketUrl="bucket_url"
                             :callback="selectEntry"
                             :visible="!entryMode.active && !showNewUserContainer"

        />

        <user-details-container :selection="entryMode.data"
                                :bucketUrl="bucket_url"
                                :callback="setEntryModeInactive"
                                :onReloadRequest="onNewUserSave"
                                :visible="entryMode.active && !showNewUserContainer"
                                :showAdvancedControls="true"

        />

        <floating-action-button :show="showFloatingButton"
                                :onclick="setShowAddContainer"
                                class="pulse"
        />

        <new-user-container :onSave="onNewUserSave"
                            :onClose="onAddContainerClose"
                            :visible="showNewUserContainer"
        />

    </div>

</template>

<script>

    import FilterBar from '@/components/FilterBar.vue'
    import LogCardsContainer from '@/components/LogCardsContainer.vue'
    import UserDetailsContainer from '@/components/UserDetailsContainer.vue'
    import FloatingActionButton from '@/components/FloatingActionButton.vue'
    import NewUserContainer from '@/components/NewUserContainer.vue'
    import { ADMIN_ENDPOINT_URL } from "../sensitivedata/aws";
    import { BUCKET_URL } from "../sensitivedata/aws";
    import { API_KEY } from "../sensitivedata/aws";

    export default {
        name: "users",
        components: {
            FilterBar,
            LogCardsContainer,
            UserDetailsContainer,
            FloatingActionButton,
            NewUserContainer
        },
        mounted() {
            M.FloatingActionButton.init(document.querySelectorAll('.fixed-action-btn'))
        },
        data() {
            return {
                bucket_url: BUCKET_URL,
                isLoading: false,
                showFloatingButton: true,
                showNewUserContainer: false,
                reckonData: [],
                lastRequestParams: {},
                entryMode: {
                    active: false,
                    data: {}
                }
            }
        },
        methods: {
            loadData: function (request) {
                this.lastRequestParams = request;
                this.isLoading = true;
                this.reckonData = [];
                request.command = 'collections';
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
                this.showFloatingButton = false;
                window.scrollTo(0, 0);
            },
            setEntryModeInactive: function () {
                this.entryMode.active = false;
                this.showFloatingButton = true;
            },
            setShowAddContainer: function () {
                this.showNewUserContainer = true;
                this.showFloatingButton = false;
                window.scrollTo(0, 0);
            },
                onNewUserSave: function () {
                this.showNewUserContainer = false;
                this.showFloatingButton = true;
                this.loadData(this.lastRequestParams);
            },
            onAddContainerClose: function () {
                this.showNewUserContainer = false;
                this.showFloatingButton = true;
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
