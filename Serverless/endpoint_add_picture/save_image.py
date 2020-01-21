from interfaces.api_phase import APIPhase


class SaveImage(APIPhase):

    def __init__(self, img_bytes: str,  invocation_id: str):

        self.img_bytes = img_bytes              # :str: Client provided image in bytes form.

        # Initializes APIPhase superclass parameters and procedures
        super(SaveImage, self).__init__(prefix='SI', phase_name='Save image', invocation_id=invocation_id)

    def run(self) -> bool:
        """
        Object's main procedure: logs current api phase, takes care of api metrics measurements, communicates with
        image saving dao and evaluates response.
        :return: boolean. Value expresses whether procedure has executed successfully or not.
        """

        # Execute request on image saving dao using given image bytes.

        # Evaluate image saving dao response status, abort if failed.

        # Procedure successful
        return True
