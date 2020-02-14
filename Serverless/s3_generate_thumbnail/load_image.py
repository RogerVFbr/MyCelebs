from interfaces.api_phase import APIPhase


class LoadImage(APIPhase):
    """
    Image loading object, responsible for preparing the file storage structure, accessing the blob storage API,
    and evaluating the response.
    """

    def __init__(self, repository, key: str, invocation_id: str):
        """
        Constructor of the load image object, stores provided and locally generated data, runs main object
        procedure.
        :param repository: selected repository to work upon.
        :param key: string containing stored image name.
        :param invocation_id: string containing id of current cloud function invocation to be to be used by API metrics.
        """

        self.repository = repository          # :*: File repository.
        self.key = key                        # :str: File name.
        self.img_bytes_io = None              # :BytesIO: Retrieved image in BytesIO form.

        # Initializes APIPhase superclass parameters and procedures
        super(LoadImage, self).__init__(prefix='SI', phase_name='Load image', invocation_id=invocation_id)

    def run(self) -> bool:
        """
        Object's main procedure: executes image loading repository procedure and evaluates response.
        :return: boolean. Value expresses whether procedure has executed successfully or not.
        """

        # Execute request on image loading infrastructure, abort if impossible.
        if not self.__load_image(): return False

        # Procedure successful
        return True

    def __load_image(self) -> bool:
        """
        Attempts to load image from repository.
        :return: boolean. Value expresses whether procedure has executed successfully or not.
        """

        # Acquire image from repository to BytesIO format.
        status, response, img_bytes_io = self.repository.load_file_as_bytes_io(self.key)

        # If unable to load image, log and abort.
        if not status:
            print('shitty request PLEASE FIX THIS LOG')
            #     self.log(self.rsc.IMAGE_LOAD_API_CONTACTED.format(response))
            return False

        # Procedure successful
        self.img_bytes_io = img_bytes_io
        self.log(self.rsc.IMAGE_LOAD_API_CONTACTED.format(response))
        return True


