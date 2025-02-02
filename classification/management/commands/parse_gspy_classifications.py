from __future__ import annotations
from cmath import e
from ctypes import sizeof
from django.core.management.base import BaseCommand, CommandError
import panoptes_client

from classification.models import Classification

class Command(BaseCommand):
    help = 'Querying the Gravity Spy Plus zooniverse project for classifications'
    def add_arguments(self, parser):
        parser.add_argument("--project-id", default='9979')
        parser.add_argument("--last-classification-id", type=int, default=None)
        parser.add_argument("--verbose", type=bool, default=True)
    #last_id reference?
    def handle(self, *args, **options):
        if options['last_classification_id'] is not None:
            all_classifications = panoptes_client.Classification.where(project_id=options['project_id'], scope='project', last_id='{0}'.format(options['last_classification_id']), page_size='100')
        else:
            all_classifications = panoptes_client.Classification.where(project_id=options['project_id'], scope='project', page_size='100')

        list_of_classification_dictionaries = []
        # Loop until no more classifications
        for iN in range(0,all_classifications.object_count):
            try:
                classification = all_classifications.next()
                list_of_classification_dictionaries.append(classification.raw)
            except:
                break

        for classification in list_of_classification_dictionaries:
            if classification['links']['workflow'] == '21793':
                classification_id=classification['id']
                #Create an annotation dictionary
                annotation_counts = [0] * 3
                for i in range(0, 3):
                    annotation_counts[i] = 0
                #Get the annotations labels based on relative y coordinate
                annotation_list = classification['annotations'][0]['value']
                height = 600 #height of a spectrum in pixel
                for j in range(len(annotation_list)):
                    y = annotation_list[j]['y']
                    if y >= height and y < 2 * height:
                        annotation_counts[0] = 1
                    elif y >= 2 * height and y <= 3 * height:
                        annotation_counts[1] = 1
                    else:
                        annotation_counts[2] = 1
                #Save all the annotation labels in the list
                annotation = []
                for k in range(len(annotation_counts)):
                    if annotation_counts[k] == 1:
                        annotation.append(k)

                workflow_id=classification['links']['workflow']
                user_id=classification['links']['user']
                subject_id=classification['links']['subjects'][0]      
                #Log on the terminal
                if options['verbose'] is True:
                    print("id is {0}".format(classification_id))
                    print("annotation is {0}".format(annotation))
                    print("workflow is {0}".format(workflow_id))
                    print("user is {0}".format(user_id))
                    print("subject is {0}".format(subject_id))

                #Instantiate the classification object
                classification_subject = Classification.objects.create_classification(classification_id=classification_id, annotation=annotation, workflow_id=workflow_id,user_id=user_id, subject_id=subject_id)
                
                #Save out the subject
                classification_subject.save()
