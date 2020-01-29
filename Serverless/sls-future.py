#    newEntriesTable:
#      Type: AWS::DynamoDB::Table
#      Properties:
#        TableName: ${self:provider.environment.NEW_ENTRIES_TABLE_NAME}
#        AttributeDefinitions:
#          - AttributeName: id
#            AttributeType: S
#          - AttributeName: time
#            AttributeType: S
#        KeySchema:
#          - AttributeName: id
#            KeyType: HASH
#          - AttributeName: time
#            KeyType: RANGE
#        ProvisionedThroughput:
#          ReadCapacityUnits: 5
#          WriteCapacityUnits: 5
#        StreamSpecification:
#          StreamViewType: NEW_IMAGE

# celeb-recognition:
#   handler: sqs_celebrity_recognition/handler.celeb_recognition
#   events:
#      - stream:
#          type: dynamodb
#          arn:
#            Fn::GetAtt:
#              - newEntriesTable
#              - StreamArn