package edu.oregonstate.mist.subjectsapi

import de.thomaskrille.dropwizard_template_config.TemplateConfigBundle
import edu.oregonstate.mist.api.BuildInfoManager
import edu.oregonstate.mist.api.Configuration
import edu.oregonstate.mist.api.Resource
import edu.oregonstate.mist.api.InfoResource
import edu.oregonstate.mist.api.AuthenticatedUser
import edu.oregonstate.mist.api.BasicAuthenticator
import edu.oregonstate.mist.subjectsapi.dao.SubjectsDAO
import edu.oregonstate.mist.subjectsapi.dao.UtilHttp
import edu.oregonstate.mist.subjectsapi.resources.SubjectResource
import io.dropwizard.client.HttpClientBuilder
import org.apache.http.client.HttpClient
import edu.oregonstate.mist.api.PrettyPrintResponseFilter
import edu.oregonstate.mist.api.jsonapi.GenericExceptionMapper
import edu.oregonstate.mist.api.jsonapi.NotFoundExceptionMapper
import io.dropwizard.Application
import io.dropwizard.auth.AuthDynamicFeature
import io.dropwizard.auth.AuthValueFactoryProvider
import io.dropwizard.auth.basic.BasicCredentialAuthFilter
import io.dropwizard.setup.Bootstrap
import io.dropwizard.setup.Environment

/**
 * Main application class.
 */
class SubjectsApplication extends Application<SubjectsConfiguration> {
    /**
     * Initializes application bootstrap.
     *
     * @param bootstrap
     */
    @Override
    public void initialize(Bootstrap<Configuration> bootstrap) {
        bootstrap.addBundle(new TemplateConfigBundle())
    }

    /**
     * Registers lifecycle managers and Jersey exception mappers
     * and container response filters
     *
     * @param environment
     * @param buildInfoManager
     */
    protected void registerAppManagerLogic(Environment environment,
                                           BuildInfoManager buildInfoManager) {

        environment.lifecycle().manage(buildInfoManager)

        environment.jersey().register(new NotFoundExceptionMapper())
        environment.jersey().register(new GenericExceptionMapper())
        environment.jersey().register(new PrettyPrintResponseFilter())
    }

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

        registerAppManagerLogic(environment, buildInfoManager)

        environment.jersey().register(new InfoResource(buildInfoManager.getInfo()))
        environment.jersey().register(new AuthDynamicFeature(
                new BasicCredentialAuthFilter.Builder<AuthenticatedUser>()
                .setAuthenticator(new BasicAuthenticator(configuration.getCredentialsList()))
                .setRealm('SkeletonApplication')
                .buildAuthFilter()
        ))
        environment.jersey().register(new AuthValueFactoryProvider.Binder
                <AuthenticatedUser>(AuthenticatedUser.class))
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
