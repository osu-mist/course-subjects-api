package edu.oregonstate.mist.subjectsapi

import edu.oregonstate.mist.api.BuildInfoManager
import edu.oregonstate.mist.api.Resource
import edu.oregonstate.mist.api.InfoResource
import edu.oregonstate.mist.api.AuthenticatedUser
import edu.oregonstate.mist.api.BasicAuthenticator
import edu.oregonstate.mist.subjectsapi.dao.SubjectsDAO
import edu.oregonstate.mist.subjectsapi.dao.UtilHttp
import edu.oregonstate.mist.subjectsapi.resources.SubjectResource
import io.dropwizard.Application
import io.dropwizard.client.HttpClientBuilder
import io.dropwizard.setup.Environment
import io.dropwizard.auth.AuthFactory
import io.dropwizard.auth.basic.BasicAuthFactory
import org.apache.http.client.HttpClient

/**
 * Main application class.
 */
class SubjectsApplication extends Application<SubjectsConfiguration> {
    /**
     * Parses command-line arguments and runs the application.
     *
     * @param configuration
     * @param environment
     */
    @Override
    public void run(SubjectsConfiguration configuration, Environment environment) {
        Resource.loadProperties()

        BuildInfoManager buildInfoManager = new BuildInfoManager()
        environment.lifecycle().manage(buildInfoManager)
        environment.jersey().register(new InfoResource(buildInfoManager.getInfo()))

        // the httpclient from DW provides with many metrics and config options
        HttpClient httpClient = new HttpClientBuilder(environment)
                .using(configuration.getHttpClientConfiguration())
                .build("backend-http-client")

        // reusable UtilHttp instance for both DAO and healthcheck
        UtilHttp utilHttp = new UtilHttp(configuration.classSearch)

        // setup dao
        SubjectsDAO subjectsDAO = new SubjectsDAO(utilHttp, httpClient)

        def classSearchResource = new SubjectResource(subjectsDAO: subjectsDAO)
        classSearchResource.setEndpointUri(configuration.getApi().getEndpointUri())
        environment.jersey().register(classSearchResource)

        environment.jersey().register(new InfoResource())
        environment.jersey().register(
                AuthFactory.binder(
                        new BasicAuthFactory<AuthenticatedUser>(
                                new BasicAuthenticator(configuration.getCredentialsList()),
                                'SubjectsApplication',
                                AuthenticatedUser.class)))
    }

    /**
     * Instantiates the application class with command-line arguments.
     *
     * @param arguments
     * @throws Exception
     */
    public static void main(String[] arguments) throws Exception {
        new SubjectsApplication().run(arguments)
    }
}
