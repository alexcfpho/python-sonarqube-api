#!/usr/bin/env python
# -*- coding:utf-8 -*-
from sonarqube.config import (
    API_MEASURES_COMPONENT_ENDPOINT,
    API_MEASURES_SEARCH_HISTORY_ENDPOINT
)


class SonarQubeMeasure:
    metricKeys = 'code_smells,bugs,vulnerabilities,new_bugs,new_vulnerabilities,new_code_smells,coverage,\
new_reliability_rating,reliability_rating,new_security_rating,security_rating,new_maintainability_rating,\
sqale_rating,tests,test_failures,test_errors,skipped_tests,test_success_density,ncloc,duplicated_lines_density,\
comment_lines_density'

    def __init__(self, sonarqube):
        self.sonarqube = sonarqube

    def get_measures_component(self, component, branch):
        """
        Return component with specified measures.
        :param component:
        :param branch:
        :return:
        """
        params = {
            'additionalFields': 'metrics,periods',
            'metricKeys': self.metricKeys,
            'component': component,
            'branch': branch
        }
        resp = self.sonarqube.make_call('get', API_MEASURES_COMPONENT_ENDPOINT, **params)
        data = resp.json()
        return data

    def get_measures_history(self, component, branch, **kwargs):
        """
        Search measures history of a component
        :param component:
        :param branch:
        :return:
        """
        params = {
            'metrics': 'code_smells,bugs,vulnerabilities,new_bugs,new_vulnerabilities,\
new_code_smells,coverage,new_coverage',
            'component': component,
            'branch': branch
        }
        if kwargs:
            self.sonarqube.copy_dict(params, kwargs)

        page_num = 1
        page_size = 1
        total = 2

        while page_num * page_size < total:
            resp = self.sonarqube.make_call('get', API_MEASURES_SEARCH_HISTORY_ENDPOINT, **params)
            response = resp.json()

            page_num = response['paging']['pageIndex']
            page_size = response['paging']['pageSize']
            total = response['paging']['total']

            params['p'] = page_num + 1

            for measure in response['measures']:
                yield measure

    def get_project_measures_component(self, project_key, branch, fc=None):
        """
        获取项目measures(可以过滤不需要的数据)
        :param project_key:
        :param branch:
        :param fc:
        :return:
        """
        if fc:
            if isinstance(fc, str):
                fc = fc.split(',')

        measures_component = self.get_measures_component(project_key, branch)['component']['measures']

        measures = {}
        for metric in measures_component:
            metric_key = metric['metric']
            if metric_key in self.metricKeys.split(','):
                measures[metric_key] = metric.get('value', None) or metric.get('periods', None)[0]['value']
                # try:
                #     measures[metric_key] = metric['value']
                # except:
                #     measures[metric_key] = metric['periods'][0]['value']

        for item in list(measures.keys()):
            if fc and item in fc:
                del measures[item]

        return measures
